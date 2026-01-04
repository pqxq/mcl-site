#!/bin/bash
# Azure App Service startup script for Django/Wagtail

set -e

echo "=== MCL Site Azure Startup ==="

# Use the Python from the venv if available
if [ -d "/home/site/wwwroot/venv" ]; then
    source /home/site/wwwroot/venv/bin/activate
    PYTHON=$(which python)
elif [ -d "/opt/python/current/bin" ]; then
    export PATH="/opt/python/current/bin:$PATH"
    PYTHON="/opt/python/current/bin/python"
else
    PYTHON=$(which python3 || which python)
fi

if [ -z "$PYTHON" ]; then
    echo "ERROR: Python not found!"
    exit 1
fi

echo "Using Python: $PYTHON"
$PYTHON --version

# Ensure pip packages are installed
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    $PYTHON -m pip install --upgrade pip > /dev/null 2>&1 || true
    $PYTHON -m pip install -r requirements.txt || echo "Some packages failed to install, continuing..."
fi

# Run database migrations
echo "Running database migrations..."
$PYTHON manage.py migrate --noinput || echo "Migrations skipped/failed (DB may not be accessible yet)"

# Collect static files
echo "Collecting static files..."
$PYTHON manage.py collectstatic --noinput || echo "Static files collection skipped"

# Start Gunicorn
echo "Starting Gunicorn server..."
GUNICORN=$($PYTHON -m pip show gunicorn >/dev/null 2>&1 && which gunicorn || echo "$PYTHON -m gunicorn")

if [ "$GUNICORN" = "" ]; then
    $PYTHON -m gunicorn mcl_site.wsgi:application \
        --bind=0.0.0.0:${PORT:-8000} \
        --workers=2 \
        --timeout=120 \
        --log-level=info \
        --access-logfile=- \
        --error-logfile=-
else
    gunicorn mcl_site.wsgi:application \
        --bind=0.0.0.0:${PORT:-8000} \
        --workers=2 \
        --timeout=120 \
        --log-level=info \
        --access-logfile=- \
        --error-logfile=-
fi
