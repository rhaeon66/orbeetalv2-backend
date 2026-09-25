import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env_value(*names: str, default: str = "") -> str:
    for name in names:
        value = os.getenv(name)
        if value not in (None, ""):
            return value
    return default


def env_bool(*names: str, default: str = "False") -> bool:
    return env_value(*names, default=default).lower() in ("true", "1", "yes")


def env_list(*names: str, default: str = "") -> list[str]:
    return [item.strip() for item in env_value(*names, default=default).split(",") if item.strip()]


SECRET_KEY = env_value("SECRET_KEY", "DJANGO_SECRET_KEY", default="django-insecure-orbeetal-local-only")
DEBUG = env_bool("DEBUG", "DJANGO_DEBUG", default="True")
ALLOWED_HOSTS = env_list(
    "ALLOWED_HOSTS",
    "DJANGO_ALLOWED_HOSTS",
    default="localhost,127.0.0.1,server.orbeetal.com",
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "core.middleware.MediaWhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"

# SQLite locally. On the VPS, .env.production sets DB_ENGINE=postgres.
if env_value("DB_ENGINE", default="sqlite").lower() in ("postgres", "postgresql"):
    _db_name = env_value("DB_NAME", "POSTGRES_DB")
    _db_user = env_value("DB_USER", "POSTGRES_USER")
    if not _db_name or not _db_user:
        from django.core.exceptions import ImproperlyConfigured

        raise ImproperlyConfigured("DB_ENGINE=postgres requires DB_NAME and DB_USER.")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _db_name,
            "USER": _db_user,
            "PASSWORD": env_value("DB_PASSWORD", "POSTGRES_PASSWORD"),
            "HOST": env_value("DB_HOST", "POSTGRES_HOST", default="127.0.0.1"),
            "PORT": env_value("DB_PORT", "POSTGRES_PORT", default="5432"),
            "CONN_MAX_AGE": 60,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

# deploy.sh runs collectstatic. Gunicorn then serves those files with WhiteNoise.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}
# Pick up uploads written after Gunicorn has already started.
WHITENOISE_AUTOREFRESH = True


def _frontend_public() -> Path:
    configured = env_value("FRONTEND_PUBLIC")
    if configured:
        return Path(configured)
    for candidate in (
        BASE_DIR.parent / "client" / "public",
        BASE_DIR.parent / "orbeetalv2-frontend" / "public",
        BASE_DIR.parent / "frontend" / "public",
    ):
        if candidate.is_dir():
            return candidate
    return BASE_DIR.parent / "client" / "public"


FRONTEND_PUBLIC = _frontend_public()

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000").rstrip("/")

CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:3000,http://127.0.0.1:3000",
)
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS",
    default="http://localhost:3000,http://127.0.0.1:3000",
)

# Session cookies are host-bound. The Next.js app on http://localhost:3000
# must call the API as http://localhost:8000 (same site, different port).
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF = True
if not DEBUG:
    # Nginx terminates TLS and proxies to Gunicorn on port 8006.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "api.permissions.BrowserSessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "api.permissions.IsStaffUser",
    ],
}
