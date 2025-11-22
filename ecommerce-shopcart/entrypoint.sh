#!/usr/bin/env sh
set -e

echo "Starting FastAPI entrypoint..."

# Docker-compose-dakı dəyişənləri istifadə et (POSTGRES_ prefix)
POSTGRES_HOST="${POSTGRES_HOST:-db-shopcart}"
DB_NAME="${POSTGRES_DB:-shopcart_db}"
DB_USER="${POSTGRES_USER:-shopcart_user}"
DB_PASSWORD="${POSTGRES_PASSWORD:-12345}"
DB_PORT="5432"

echo "Database configuration:"
echo "Host: $POSTGRES_HOST"
echo "Database: $DB_NAME" 
echo "User: $DB_USER"
echo "Port: $DB_PORT"

# Wait for Postgres
for i in $(seq 1 30); do
  if pg_isready -h "$POSTGRES_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME"; then
    echo "Postgres is ready!"
    break
  fi
  echo "Waiting for Postgres... ($i/30)"
  sleep 2
done

# Check if we should run migrations
if [ "$SKIP_MIGRATIONS" != "true" ]; then
  echo "Running migrations..."
  alembic upgrade head || { echo "Migration failed!"; exit 1; }
else
  echo "Skipping migrations (SKIP_MIGRATIONS=true)"
fi

# Start FastAPI
if [ "$ENV" = "development" ]; then
  echo "Running in development mode with reload..."
  exec uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000} --reload
else
  echo "Running in production mode..."
  exec uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers
fi