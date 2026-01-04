from .base import *
import os
import dj_database_url

# --------------------------------------------------
# BASIC
# --------------------------------------------------

DEBUG = False

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required in production")

# --------------------------------------------------
# HOSTS
# --------------------------------------------------

ALLOWED_HOSTS = [
    "mcl-mk.azurewebsites.net",
    ".azurewebsites.net",
]

if os.environ.get("WEBSITE_HOSTNAME"):
    ALLOWED_HOSTS.append(os.environ["WEBSITE_HOSTNAME"])

# Add custom domain if configured
if os.environ.get("CUSTOM_DOMAIN"):
    ALLOWED_HOSTS.append(os.environ["CUSTOM_DOMAIN"])

# --------------------------------------------------
# CSRF / HTTPS / AZURE FIX (CRITICAL)
# --------------------------------------------------

CSRF_TRUSTED_ORIGINS = [
    "https://mcl-mk.azurewebsites.net",
]

if os.environ.get("WEBSITE_HOSTNAME"):
    CSRF_TRUSTED_ORIGINS.append(f"https://{os.environ['WEBSITE_HOSTNAME']}")

if os.environ.get("CUSTOM_DOMAIN"):
    CSRF_TRUSTED_ORIGINS.append(f"https://{os.environ['CUSTOM_DOMAIN']}")

# Azure works behind reverse proxy
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

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

# --------------------------------------------------
# WAGTAIL
# --------------------------------------------------

WAGTAILADMIN_BASE_URL = os.environ.get(
    "WAGTAILADMIN_BASE_URL", 
    f"https://{os.environ.get('WEBSITE_HOSTNAME', 'mcl-mk.azurewebsites.net')}"
)

# --------------------------------------------------
# LOGGING
# --------------------------------------------------

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

# Azure Application Insights (optional)
if os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING"):
    MIDDLEWARE.insert(0, "opencensus.ext.django.middleware.OpencensusMiddleware")
    OPENCENSUS = {
        "TRACE": {
            "SAMPLER": "opencensus.trace.samplers.ProbabilitySampler(rate=1)",
            "EXPORTER": f"opencensus.ext.azure.trace_exporter.AzureExporter(connection_string='{os.environ.get('APPLICATIONINSIGHTS_CONNECTION_STRING')}')",
        }
    }

# --------------------------------------------------
# CACHING (Azure Redis Cache - optional)
# --------------------------------------------------

if os.environ.get("REDIS_URL"):
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": os.environ.get("REDIS_URL"),
        }
    }
