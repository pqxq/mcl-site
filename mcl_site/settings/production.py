from .base import *
import os

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
