#!/bin/bash
# Azure App Service startup script for Django/Wagtail

set -e

echo "=== MCL Site Azure Startup ==="

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files (in case not done during build)
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Start Gunicorn
echo "Starting Gunicorn server..."
exec gunicorn mcl_site.wsgi:application \
    --bind=0.0.0.0:${PORT:-8000} \
    --workers=${GUNICORN_WORKERS:-2} \
    --threads=${GUNICORN_THREADS:-4} \
    --worker-class=gthread \
    --worker-tmp-dir=/dev/shm \
    --timeout=120 \
    --keep-alive=5 \
    --log-level=info \
    --access-logfile=- \
    --error-logfile=-
