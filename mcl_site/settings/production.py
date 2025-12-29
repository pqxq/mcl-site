from .base import *
import os

# Add WhiteNoise to MIDDLEWARE (must be early in the list)
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware", # Add this
    # ... other middleware
]

# Static files (CSS/JS)
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files (Images/Docs) - REQUIRED for App Platform
# You must set these env vars in DigitalOcean
if os.environ.get("USE_SPACES"):
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_ENDPOINT_URL = os.environ.get("AWS_S3_ENDPOINT_URL")
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    AWS_LOCATION = 'media'
    STORAGES = {
        "default": {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"},
        "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
    }

DEBUG = False

SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "example.com").split(",")

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
# Use PostgreSQL in production
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "mcl_db"),
        "USER": os.environ.get("DB_USER", "mcl_user"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "password"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}



try:
    from .local import *
except ImportError:
    pass
