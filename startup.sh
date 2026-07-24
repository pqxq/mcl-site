#!/bin/bash
# Railway startup script for Django/Wagtail
set -e

echo "=== MCL Site Railway Startup ==="

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files (in case build-time collect failed)
echo "Collecting static files..."
python manage.py collectstatic --noinput 2>/dev/null || true

# Create cache table if it doesn't exist
echo "Creating cache table..."
python manage.py createcachetable 2>/dev/null || true

# Start Gunicorn
echo "Starting Gunicorn on port ${PORT:-8000}..."
exec gunicorn mcl_site.wsgi:application \
    --bind=0.0.0.0:${PORT:-8000} \
    --workers=2 \
    --timeout=120 \
    --log-level=info \
    --access-logfile=- \
    --error-logfile=-
