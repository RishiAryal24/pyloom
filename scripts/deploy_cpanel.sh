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
  PYTHON_BIN="$(find -L "$HOME/virtualenv" -path "*/$PROJECT_NAME/*/bin/python" -executable 2>/dev/null | head -n 1)"
fi

if [ -z "$PYTHON_BIN" ]; then
  echo "No cPanel Python virtualenv was found."
  echo "Create the cPanel Python App first, then redeploy."
  echo "Use startup file: passenger_wsgi.py"
  echo "Use entry point: application"
  exit 1
fi

"$PYTHON_BIN" -m pip install -r requirements.txt
"$PYTHON_BIN" manage.py migrate --noinput
"$PYTHON_BIN" manage.py collectstatic --noinput

touch tmp/restart.txt

echo "Deployment complete."
