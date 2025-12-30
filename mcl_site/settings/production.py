from .base import *
import os
import dj_database_url

DEBUG = False

# 1. Security & Hosts
SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
# Azure provides the domain in WEBSITE_HOSTNAME
ALLOWED_HOSTS = [os.environ.get("WEBSITE_HOSTNAME")] if os.environ.get("WEBSITE_HOSTNAME") else os.environ.get("ALLOWED_HOSTS", "example.com").split(",")
CSRF_TRUSTED_ORIGINS = [f"https://{host}" for host in ALLOWED_HOSTS]

# 2. Database (PostgreSQL)
# Azure provides connection details via DATABASE_URL or individual params.
# We will construct the URL if Azure provides individual params (common in Flexible Server).
DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get("DATABASE_URL"),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# 3. Static Files (CSS/JS) - Served via WhiteNoise
try:
    MIDDLEWARE.remove("django.middleware.security.SecurityMiddleware")
except ValueError:
    pass

MIDDLEWARE.insert(0, "django.middleware.security.SecurityMiddleware")
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# 4. Media Files (Images) - Azure Blob Storage
if os.environ.get("AZURE_ACCOUNT_NAME"):
    AZURE_ACCOUNT_NAME = os.environ.get("AZURE_ACCOUNT_NAME")
    AZURE_ACCOUNT_KEY = os.environ.get("AZURE_ACCOUNT_KEY")
    AZURE_CONTAINER = os.environ.get("AZURE_CONTAINER", "media")
    AZURE_CUSTOM_DOMAIN = f'{AZURE_ACCOUNT_NAME}.blob.core.windows.net'
    
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.azure_storage.AzureStorage",
            "OPTIONS": {
                "timeout": 20,
                "expiration_secs": None,
            },
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }