#!/bin/sh
# docker-entrypoint.sh
# Runs before the app starts. On cloud deploys (e.g. Render), if DATA_DOWNLOAD_URL
# is set and the DB doesn't exist yet, downloads and extracts it.
# On local docker-compose (data/ is volume-mounted), this is a no-op.

set -e

DB_FILE="${DB_PATH:-/app/data/credit_risk.db}"
DATA_DIR=$(dirname "$DB_FILE")

# Only download if the DB is missing AND a download URL is configured
if [ -n "$DATA_DOWNLOAD_URL" ] && [ ! -f "$DB_FILE" ]; then
  echo "[entrypoint] DB not found. Downloading from: $DATA_DOWNLOAD_URL"
  mkdir -p "$DATA_DIR"
  curl -fSL "$DATA_DOWNLOAD_URL" -o "$DATA_DIR/credit_risk_db.zip"
  echo "[entrypoint] Extracting archive..."
  python3 -c "
import zipfile, os
with zipfile.ZipFile('$DATA_DIR/credit_risk_db.zip', 'r') as z:
    z.extractall('$DATA_DIR')
os.remove('$DATA_DIR/credit_risk_db.zip')
"
  echo "[entrypoint] DB ready at: $DB_FILE"
else
  if [ -f "$DB_FILE" ]; then
    echo "[entrypoint] DB already present at: $DB_FILE — skipping download."
  fi
fi

# Ensure src.* and backend.* packages are importable by the venv Python
export PYTHONPATH=/app

# Hand off to the main process (CMD from Dockerfile)
exec "$@"
