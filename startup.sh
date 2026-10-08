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

# Memory allocation optimizations (jemalloc & glibc arena tuning)
JEMALLOC_LIB=$(find /usr/lib -name "libjemalloc.so.2" 2>/dev/null | head -n 1)
if [ -n "$JEMALLOC_LIB" ]; then
    echo "Enabling jemalloc from $JEMALLOC_LIB"
    export LD_PRELOAD="$JEMALLOC_LIB"
fi
export MALLOC_ARENA_MAX=${MALLOC_ARENA_MAX:-2}
export MALLOC_TRIM_THRESHOLD_=${MALLOC_TRIM_THRESHOLD_:-100000}

# Worker and concurrency settings tailored to minimize memory usage
WORKERS=${WEB_CONCURRENCY:-${GUNICORN_WORKERS:-2}}
THREADS=${GUNICORN_THREADS:-2}
MAX_REQUESTS=${GUNICORN_MAX_REQUESTS:-1000}
MAX_REQUESTS_JITTER=${GUNICORN_MAX_REQUESTS_JITTER:-100}

# Start Gunicorn with memory recycling, threading, and copy-on-write preloading
echo "Starting Gunicorn on port ${PORT:-8000} with ${WORKERS} workers, ${THREADS} threads, preload..."
exec gunicorn mcl_site.wsgi:application \
    --bind=0.0.0.0:${PORT:-8000} \
    --workers=${WORKERS} \
    --threads=${THREADS} \
    --worker-class=gthread \
    --preload \
    --max-requests=${MAX_REQUESTS} \
    --max-requests-jitter=${MAX_REQUESTS_JITTER} \
    --timeout=120 \
    --log-level=info \
    --access-logfile=- \
    --error-logfile=-
