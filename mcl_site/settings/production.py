from .base import *
import os
import dj_database_url

DEBUG = False

# 1. Security & Hosts
SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")

# Отримуємо хост з Azure або змінних середовища
if os.environ.get("WEBSITE_HOSTNAME"):
    ALLOWED_HOSTS = [os.environ.get("WEBSITE_HOSTNAME")]
else:
    ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "mcl-mk.azurewebsites.net").split(",")

# === ВАЖЛИВО: Налаштування CSRF для Azure ===
# Додаємо ваш домен у довірені джерела. 
# Це вирішує помилку "Origin checking failed"
CSRF_TRUSTED_ORIGINS = [
    "https://mcl-mk.azurewebsites.net",
]
# Якщо є WEBSITE_HOSTNAME, додаємо і його (для надійності)
if os.environ.get("WEBSITE_HOSTNAME"):
    CSRF_TRUSTED_ORIGINS.append(f"https://{os.environ.get('WEBSITE_HOSTNAME')}")

# === ВАЖЛИВО: HTTPS за проксі Azure ===
# Azure App Service працює за Load Balancer, тому Django може "думати", що працює по HTTP.
# Цей рядок каже Django довіряти заголовку X-Forwarded-Proto.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# 2. Database (PostgreSQL)
DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get("DATABASE_URL"),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# 3. Static Files (WhiteNoise)
try:
    MIDDLEWARE.remove("django.middleware.security.SecurityMiddleware")
except ValueError:
    pass

MIDDLEWARE.insert(0, "django.middleware.security.SecurityMiddleware")
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# 4. Media Files (Azure Blob Storage)
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