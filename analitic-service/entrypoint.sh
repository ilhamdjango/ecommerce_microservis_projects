#!/usr/bin/env sh
set -e

echo "=== Starting entrypoint ==="

# --- DB host təyini ---
export DB_HOST=${POSTGRES_HOST:-db-analytic}
export DB_USER=${POSTGRES_USER:-analytic_user}
export DB_NAME=${POSTGRES_DB:-analytic_db}
export DB_PASSWORD=${POSTGRES_PASSWORD:-12345}
export DB_PORT=${POSTGRES_PORT:-5432}

# --- Gunicorn port ---
export APP_PORT=${PORT:-8006}

echo "Using Postgres:"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  DB: $DB_NAME"
echo "  User: $DB_USER"

# --- Wait for Postgres ---
echo "Waiting for Postgres to be ready..."
until nc -z $DB_HOST $DB_PORT; do
  echo "Postgres is unavailable - sleeping"
  sleep 2
done

echo "Postgres is up - continuing..."

# --- Django Migrate ---
echo "Running Django migrations..."
python manage.py migrate --noinput

# --- Static files toplamaq ---
echo "Collecting static files..."
python manage.py collectstatic --noinput

# --- Superuser yaratmaq (non-interactive) ---
echo "Creating superuser if not exists..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
username = 'ilham'
email = 'ilham@example.com'
password = 'ecommerce'
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
"

# --- Gunicorn serverini işə sal ---
echo "Starting Gunicorn on 0.0.0.0:${APP_PORT}..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${APP_PORT} \
    --workers 2 \
    --threads 2 \
    --timeout 0 \
    --access-logfile - \
    --error-logfile -
