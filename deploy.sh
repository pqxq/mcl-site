#!/bin/bash
set -e

echo "=== MCL Site Deployment Script ==="

# Get Python path
PYTHON=$(which python3 || which python)
if [ -z "$PYTHON" ]; then
    echo "ERROR: Python not found!"
    exit 1
fi

echo "Using Python: $PYTHON"
$PYTHON --version

# Install dependencies  
echo "Installing Python packages..."
$PYTHON -m pip install --upgrade pip setuptools wheel > /dev/null 2>&1
$PYTHON -m pip install -r requirements.txt

# Run migrations
echo "Running database migrations..."
$PYTHON manage.py migrate --noinput || echo "Migrations failed (DB may not be ready)"

# Collect static files
echo "Collecting static files..."
$PYTHON manage.py collectstatic --noinput --clear || echo "Static files collection failed"

echo "Deployment complete!"
