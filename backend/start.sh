#!/bin/sh

set -e

echo "Waiting for database..."
python - <<'PY'
import time
import os
import psycopg2

dsn = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/traffic')
for _ in range(20):
    try:
        conn = psycopg2.connect(dsn)
        conn.close()
        break
    except Exception:
        time.sleep(1)
else:
    raise SystemExit('Database is not reachable')
PY

echo "Running migrations"
python -m app.db.init_db

exec "$@"
