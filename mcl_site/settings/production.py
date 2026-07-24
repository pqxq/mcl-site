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
    "ml9.mk.ua",
    "www.ml9.mk.ua",
    "healthcheck.railway.app",
]

# Allow Railway's auto-generated domain
railway_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN")
if railway_domain:
    ALLOWED_HOSTS.append(railway_domain)

# Allow additional custom hosts via env var
extra_host = os.environ.get("ALLOWED_HOST")
if extra_host:
    ALLOWED_HOSTS.append(extra_host)

# --------------------------------------------------
# CSRF / HTTPS
# --------------------------------------------------

CSRF_TRUSTED_ORIGINS = [
    "https://ml9.mk.ua",
    "https://www.ml9.mk.ua",
]

if railway_domain:
    CSRF_TRUSTED_ORIGINS.append(f"https://{railway_domain}")

# Railway terminates TLS at the proxy level and forwards
# requests over HTTP internally. We must NOT redirect to HTTPS
# ourselves or it will cause an infinite redirect loop.
SECURE_SSL_REDIRECT = False

# Trust Railway's proxy header so request.is_secure() works correctly.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Additional security headers
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# --------------------------------------------------
# DATABASE (PostgreSQL via Railway)
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

if railway_domain:
    WAGTAILADMIN_BASE_URL = f"https://{railway_domain}"
else:
    WAGTAILADMIN_BASE_URL = "https://ml9.mk.ua"

# Override with explicit env var if set
_base_url = os.environ.get("WAGTAILADMIN_BASE_URL")
if _base_url:
    WAGTAILADMIN_BASE_URL = _base_url

# --------------------------------------------------
# LOGGING (console-only for Railway)
# --------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "wagtail": {
            "handlers": ["console"],
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
