# Use an official Python runtime as a parent image.
FROM python:3.11-slim

# Add user that will be used in the container.
RUN useradd wagtail

# Port used by this container to serve HTTP.
EXPOSE 8000

# Set environment variables.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    DJANGO_SETTINGS_MODULE=mcl_site.settings.production

# Install system packages required by Wagtail and Django.
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
 && rm -rf /var/lib/apt/lists/*

# Use /app folder as a directory where the source code is stored.
WORKDIR /app

# Install the project requirements.
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code of the project into the container.
COPY . /app/

# Create media directory and set ownership
RUN mkdir -p /app/staticfiles /app/media && chown -R wagtail:wagtail /app

# Use user "wagtail" to run the build commands below and the server itself.
USER wagtail

# Collect static files at build time.
RUN python manage.py collectstatic --noinput --clear 2>/dev/null || true

# Runtime command — use startup.sh for migrations + gunicorn
CMD ["bash", "/app/startup.sh"]
