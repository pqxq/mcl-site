#!/bin/bash
# Azure App Service startup script for Django/Wagtail

echo "=== MCL Site Azure Startup ==="

# Run database migrations (ignore errors if DB not accessible yet)
echo "Running database migrations..."
python manage.py migrate --noinput || echo "Migration failed, continuing..."

# Start Gunicorn
echo "Starting Gunicorn server..."
gunicorn mcl_site.wsgi:application \
    --bind=0.0.0.0:${PORT:-8000} \
    --workers=2 \
    --timeout=120 \
    --log-level=info \
    --access-logfile=- \
    --error-logfile=-
