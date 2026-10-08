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
    "ml9-website-production.up.railway.app",
    "localhost",
    "127.0.0.1",
]

# Allow Railway's auto-generated domain
railway_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN")
if railway_domain and railway_domain not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(railway_domain)

# Allow additional custom hosts via env var (single, comma-separated, or Cloudflare domain)
extra_hosts = (
    os.environ.get("ALLOWED_HOSTS")
    or os.environ.get("ALLOWED_HOST")
    or os.environ.get("CLOUDFLARE_DOMAIN")
)
if extra_hosts:
    for host in extra_hosts.split(","):
        host = host.strip()
        if host and host not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(host)

# --------------------------------------------------
# CSRF / HTTPS
# --------------------------------------------------

CSRF_TRUSTED_ORIGINS = [
    "https://ml9.mk.ua",
    "https://www.ml9.mk.ua",
]

if railway_domain:
    origin = f"https://{railway_domain}"
    if origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(origin)

extra_csrf = os.environ.get("CSRF_TRUSTED_ORIGINS")
if extra_csrf:
    for o in extra_csrf.split(","):
        o = o.strip()
        if o and o not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(o)
elif extra_hosts:
    for host in extra_hosts.split(","):
        host = host.strip()
        if host and not host.startswith("."):
            origin = host if host.startswith("http") else f"https://{host}"
            if origin not in CSRF_TRUSTED_ORIGINS:
                CSRF_TRUSTED_ORIGINS.append(origin)

# Railway and Cloudflare terminate TLS at the edge/proxy level and forward
# requests over HTTP internally. We must NOT redirect to HTTPS
# ourselves or it will cause an infinite redirect loop.
SECURE_SSL_REDIRECT = False

# Trust proxy header so request.is_secure() works correctly with Cloudflare & Railway.
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
            conn_max_age=int(os.environ.get("CONN_MAX_AGE", 60)),
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
    "core.middleware.CloudflareMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    *MIDDLEWARE,
]

# --------------------------------------------------
# STATIC FILES (WhiteNoise optimized for memory & edge caching)
# --------------------------------------------------

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)
WHITENOISE_MAX_AGE = 31536000
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_KEEP_ONLY_HASHED_FILES = True

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
# CACHING (Offload from Python worker RAM to Redis or Database)
# --------------------------------------------------

redis_url = os.environ.get("REDIS_URL") or os.environ.get("CACHE_URL")
if redis_url:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": redis_url,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "IGNORE_EXCEPTIONS": True,
            },
            "TIMEOUT": 3600,
        }
    }
else:
    # Use DatabaseCache to keep worker RSS memory footprint minimal
    # (Table django_cache is created by `python manage.py createcachetable` in startup.sh)
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.db.DatabaseCache",
            "LOCATION": "django_cache",
            "TIMEOUT": 3600,
            "OPTIONS": {
                "MAX_ENTRIES": 1000,
                "CULL_FREQUENCY": 3,
            },
        }
    }

