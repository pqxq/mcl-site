from .base import *
import os

DEBUG = False
SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "example.com").split(",")

# === 1. Додайте це для роботи HTTPS на DigitalOcean ===
CSRF_TRUSTED_ORIGINS = [f"https://{host}" for host in ALLOWED_HOSTS]

# === 2. Налаштування бази даних (вже є) ===
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

# === 3. Статичні файли (CSS/JS) через WhiteNoise ===
# Додайте WhiteNoise одразу після SecurityMiddleware
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# === 4. Медіа файли (Картинки) через DO Spaces / AWS S3 ===
# Якщо змінні середовища задані, використовуємо хмарне сховище
if os.environ.get("AWS_ACCESS_KEY_ID"):
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_ENDPOINT_URL = os.environ.get("AWS_S3_ENDPOINT_URL") # Наприклад: https://fra1.digitaloceanspaces.com
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    AWS_LOCATION = 'media'
    AWS_S3_REGION_NAME = 'fra1' # Або ваш регіон
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    
    # Новий формат налаштування сховищ у Django 4.2+
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage"
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
        },
    }