from .base import *
import os
import dj_database_url
from django.core.exceptions import ImproperlyConfigured

# --------------------------------------------------
# BASIC
# --------------------------------------------------

DEBUG = False

secret = os.environ.get("SECRET_KEY")
if not secret:
    raise ImproperlyConfigured("SECRET_KEY environment variable is required")
SECRET_KEY = secret

# --------------------------------------------------
# HOSTS
# --------------------------------------------------

ALLOWED_HOSTS = [
    "velychko.pythonanywhere.com",
]

# --------------------------------------------------
# CSRF / HTTPS
# --------------------------------------------------

CSRF_TRUSTED_ORIGINS = [
    "https://velychko.pythonanywhere.com",
]

SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Additional security headers
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# --------------------------------------------------
# DATABASE
# --------------------------------------------------

if os.environ.get("DATABASE_URL"):
    DATABASES = {
        "default": dj_database_url.config(
            default=os.environ["DATABASE_URL"],
            conn_max_age=600,
            conn_health_checks=True,
        )
    }

# --------------------------------------------------
# MIDDLEWARE (ORDER IS IMPORTANT)
# --------------------------------------------------

# Remove SecurityMiddleware if exists (base.py)
try:
    MIDDLEWARE.remove("django.middleware.security.SecurityMiddleware")
except ValueError:
    pass

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    *MIDDLEWARE,
]

# --------------------------------------------------
# STATIC FILES
# --------------------------------------------------

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)

# --------------------------------------------------
# MEDIA FILES
# --------------------------------------------------

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

# --------------------------------------------------
# WAGTAIL
# --------------------------------------------------

WAGTAILADMIN_BASE_URL = os.environ.get(
    "WAGTAILADMIN_BASE_URL", 
    "https://velychko.pythonanywhere.com"
)

# --------------------------------------------------
# LOGGING
# --------------------------------------------------

LOG_DIR = os.environ.get("DJANGO_LOG_DIR", "/home/LogFiles")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "verbose",
            "filename": os.path.join(LOG_DIR, "django.log"),
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 2,
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "wagtail": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# --------------------------------------------------
# CACHING
# --------------------------------------------------

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache_table",
    }
}
