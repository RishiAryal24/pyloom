#!/bin/bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$APP_DIR"

mkdir -p staticfiles media logs tmp

PYTHON_BIN=""

if [ -n "$VIRTUAL_ENV" ] && [ -x "$VIRTUAL_ENV/bin/python" ]; then
  PYTHON_BIN="$VIRTUAL_ENV/bin/python"
elif [ -d "$HOME/virtualenv" ]; then
  PROJECT_NAME="$(basename "$APP_DIR")"
  PYTHON_BIN="$(find -L "$HOME/virtualenv" -path "*/$PROJECT_NAME/*/bin/python" -executable 2>/dev/null | head -n 1)"
fi

if [ -z "$PYTHON_BIN" ]; then
  echo "No cPanel Python virtualenv was found."
  echo "Create the cPanel Python App first, then redeploy."
  echo "Use startup file: passenger_wsgi.py"
  echo "Use entry point: application"
  exit 1
fi

PUBLIC_ROOT="${PUBLIC_ROOT:-$HOME/public_html}"
HEALTHCHECK_URL="${DEPLOY_HEALTH_URL:-https://pyloomtech.com/health/}"

ensure_public_link() {
  local source_path="$1"
  local link_path="$2"

  mkdir -p "$(dirname "$link_path")"

  if [ -L "$link_path" ]; then
    ln -sfn "$source_path" "$link_path"
  elif [ -e "$link_path" ]; then
    echo "Cannot create $link_path: an existing non-symlink path is present."
    echo "Move or remove that path manually, then redeploy."
    exit 1
  else
    ln -s "$source_path" "$link_path"
  fi
}

"$PYTHON_BIN" -m pip install -r requirements.txt
"$PYTHON_BIN" -m py_compile passenger_wsgi.py
"$PYTHON_BIN" -c "import passenger_wsgi; assert callable(passenger_wsgi.application)"
"$PYTHON_BIN" manage.py check
"$PYTHON_BIN" manage.py migrate --noinput
"$PYTHON_BIN" manage.py collectstatic --noinput

ensure_public_link "$APP_DIR/staticfiles" "$PUBLIC_ROOT/static"
ensure_public_link "$APP_DIR/media" "$PUBLIC_ROOT/media"

touch tmp/restart.txt

if [ -d "$PUBLIC_ROOT/tmp" ]; then
  touch "$PUBLIC_ROOT/tmp/restart.txt"
fi

if [ "${SKIP_HTTP_HEALTHCHECK:-0}" != "1" ]; then
  if ! command -v curl >/dev/null 2>&1; then
    echo "curl is unavailable; set SKIP_HTTP_HEALTHCHECK=1 to skip HTTP verification."
    exit 1
  fi

  health_ok=0
  for attempt in 1 2 3 4 5; do
    if curl --fail --silent --show-error --max-time 15 "$HEALTHCHECK_URL" >/dev/null; then
      health_ok=1
      break
    fi
    echo "Health check attempt $attempt failed; retrying..."
    sleep 3
  done

  if [ "$health_ok" -ne 1 ]; then
    echo "Deployment finished, but $HEALTHCHECK_URL did not return HTTP 2xx."
    exit 1
  fi
fi

echo "Deployment complete. Passenger, Django, static files, media, and health check verified."
