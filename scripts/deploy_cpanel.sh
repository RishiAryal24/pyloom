#!/bin/bash
set -e

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$APP_DIR"

mkdir -p staticfiles media logs tmp

PYTHON_BIN=""

if [ -n "$VIRTUAL_ENV" ] && [ -x "$VIRTUAL_ENV/bin/python" ]; then
  PYTHON_BIN="$VIRTUAL_ENV/bin/python"
elif [ -d "$HOME/virtualenv" ]; then
  PROJECT_NAME="$(basename "$APP_DIR")"
  PYTHON_BIN="$(find "$HOME/virtualenv" -path "*/$PROJECT_NAME/*/bin/python" -type f -executable 2>/dev/null | head -n 1)"
fi

if [ -z "$PYTHON_BIN" ]; then
  echo "No cPanel Python virtualenv was found."
  echo "Create the cPanel Python App first, then redeploy."
  echo "Use startup file: passenger_wsgi.py"
  echo "Use entry point: application"
  exit 1
fi

PUBLIC_ROOT="${PUBLIC_ROOT:-$HOME/public_html}"
HTACCESS_FILE="$PUBLIC_ROOT/.htaccess"
PASSENGER_BLOCK_START="# BEGIN PYLOOM PASSENGER"
PASSENGER_BLOCK_END="# END PYLOOM PASSENGER"

"$PYTHON_BIN" -m pip install -r requirements.txt
"$PYTHON_BIN" manage.py migrate --noinput
"$PYTHON_BIN" manage.py collectstatic --noinput

mkdir -p "$PUBLIC_ROOT"
touch "$HTACCESS_FILE"

# Keep unrelated cPanel rules while refreshing this project's Passenger mapping.
HTACCESS_TMP="$(mktemp)"
awk -v start="$PASSENGER_BLOCK_START" -v end="$PASSENGER_BLOCK_END" '
    $0 == start { skip = 1; next }
    $0 == end { skip = 0; next }
    skip { next }
    $1 == "PassengerAppRoot" { next }
    $1 == "PassengerBaseURI" { next }
    $1 == "PassengerPython" { next }
    { print }
' "$HTACCESS_FILE" > "$HTACCESS_TMP"

cat >> "$HTACCESS_TMP" <<EOF

$PASSENGER_BLOCK_START
PassengerAppRoot "$APP_DIR"
PassengerBaseURI "/"
PassengerPython "$PYTHON_BIN"
$PASSENGER_BLOCK_END
EOF

mv "$HTACCESS_TMP" "$HTACCESS_FILE"
chmod 644 "$HTACCESS_FILE"

# A legacy static homepage takes precedence over Passenger on some cPanel hosts.
if [ -f "$PUBLIC_ROOT/index.html" ]; then
  BACKUP_INDEX="$PUBLIC_ROOT/index.html.pre-passenger"
  if [ ! -e "$BACKUP_INDEX" ]; then
    mv "$PUBLIC_ROOT/index.html" "$BACKUP_INDEX"
    echo "Moved legacy public_html/index.html to index.html.pre-passenger."
  else
    echo "Warning: $PUBLIC_ROOT/index.html still exists; remove or rename it manually."
  fi
fi

touch tmp/restart.txt

echo "Deployment complete. Passenger is mapped to $APP_DIR at /."
