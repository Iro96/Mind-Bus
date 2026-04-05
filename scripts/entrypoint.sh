#!/bin/sh
set -e

if [ -n "$DATABASE_URL" ]; then
  echo "Initializing database..."
  python /app/scripts/init_db.py
fi

exec "$@"
