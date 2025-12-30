from .base import *
import os
import dj_database_url

# --------------------------------------------------
# BASIC
# --------------------------------------------------

DEBUG = False

SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")

# --------------------------------------------------
# HOSTS
# --------------------------------------------------

ALLOWED_HOSTS = [
    "mcl-mk.azurewebsites.net",
]

if os.environ.get("WEBSITE_HOSTNAME"):
    ALLOWED_HOSTS.append(os.environ["WEBSITE_HOSTNAME"])

# --------------------------------------------------
# CSRF / HTTPS / AZURE FIX (CRITICAL)
# --------------------------------------------------

CSRF_TRUSTED_ORIGINS = [
    "https://mcl-mk.azurewebsites.net",
]

if os.environ.get("WEBSITE_HOSTNAME"):
    CSRF_TRUSTED_ORIGINS.append(f"https://{os.environ['WEBSITE_HOSTNAME']}")

# Azure works behind reverse proxy
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# --------------------------------------------------
# DATABASE
# --------------------------------------------------

DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get("DATABASE_URL"),
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
# MEDIA FILES (AZURE BLOB)
# --------------------------------------------------

if os.environ.get("AZURE_ACCOUNT_NAME"):
    AZURE_ACCOUNT_NAME = os.environ.get("AZURE_ACCOUNT_NAME")
    AZURE_ACCOUNT_KEY = os.environ.get("AZURE_ACCOUNT_KEY")
    AZURE_CONTAINER = os.environ.get("AZURE_CONTAINER", "media")
    AZURE_CUSTOM_DOMAIN = f"{AZURE_ACCOUNT_NAME}.blob.core.windows.net"

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
