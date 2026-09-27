from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-key-change-in-production")
# Default to False for safety in production; set DEBUG=True explicitly for local dev.
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,.localhost").split(",")
    if h.strip()
]

# Shared apps (tables in public + all tenant schemas)
SHARED_APPS = (
    "django_tenants",
    "tenants",
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.admin",
    "django.contrib.staticfiles",
)

# Tenant apps (tables in tenant schemas only)
TENANT_APPS = (
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.admin",
    "accounts",
    "products",
    "orders",
)

INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]

DATABASES = {
    "default": {
        "ENGINE": "django_tenants.postgresql_backend",
        "NAME": os.getenv("POSTGRES_DB", "restromandu_demo"),
        "USER": os.getenv("POSTGRES_USER", "postgres"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "postgres"),
        "HOST": os.getenv("POSTGRES_HOST", "127.0.0.1"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": 60,
    }
}
DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)

TENANT_MODEL = "tenants.Client"
TENANT_DOMAIN_MODEL = "tenants.Domain"
PUBLIC_SCHEMA_URLCONF = "config.urls_public"

MIDDLEWARE = [
    "django_tenants.middleware.main.TenantMainMiddleware",
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise serves static files efficiently in production
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

from django.core.exceptions import ImproperlyConfigured

# Password Validation (enabled in production when DEBUG=False)
if not DEBUG:
    AUTH_PASSWORD_VALIDATORS = [
        {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
        {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
        {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
        {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    ]
    # Safety check: require a real SECRET_KEY in production
    if not SECRET_KEY or SECRET_KEY == "dev-only-secret-key-change-in-production":
        raise ImproperlyConfigured("SECRET_KEY must be set to a secure value when DEBUG=False")
else:
    AUTH_PASSWORD_VALIDATORS = []

# Production security defaults (only applied when DEBUG is False)
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kathmandu"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
# Use WhiteNoise for static file serving in production
if not DEBUG:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

SESSION_COOKIE_NAME = "restromandu_session"
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Tenant domain configuration
# Base domain used for tenant subdomains (e.g. 'localhost' -> subdomain.localhost)
TENANT_DOMAIN_BASE = os.getenv("TENANT_DOMAIN_BASE", "localhost")
# Optional single public tenant domain (if set, maps to public schema)
PUBLIC_TENANT_DOMAIN = os.getenv("PUBLIC_TENANT_DOMAIN", "")

# Ensure ALLOWED_HOSTS includes tenant domains and public domain
if PUBLIC_TENANT_DOMAIN:
    if PUBLIC_TENANT_DOMAIN not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(PUBLIC_TENANT_DOMAIN)

# Allow subdomains for TENANT_DOMAIN_BASE, and the base itself
base = TENANT_DOMAIN_BASE.lstrip('.') if TENANT_DOMAIN_BASE else ''
# If the configured base used a two-level namespace like 'tenants.restromandu.com',
# normalize to the root domain so ALLOWED_HOSTS includes '*.restromandu.com'.
if base.startswith('tenants.'):
    base = base.split('.', 1)[1]
if base:
    wildcard = f".{base}"
    if wildcard not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(wildcard)
    if base not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(base)

# Basic production logging
if not DEBUG:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"}
        },
        "handlers": {
            "console": {"class": "logging.StreamHandler", "formatter": "standard"}
        },
        "root": {"handlers": ["console"], "level": "INFO"},
    }
