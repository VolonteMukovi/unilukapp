"""
Configuration Django — variables sensibles via fichier .env (voir .env.example).
Le fichier `.env` est chargé dans `config.__init__` avant l'import de ce module.
"""

import logging
import os
from datetime import timedelta
from pathlib import Path

from config.schema import TAG_DESCRIPTIONS, TAG_ORDER

BASE_DIR = Path(__file__).resolve().parent.parent


def _int_env(key: str, default: int) -> int:
    raw = os.environ.get(key, "").strip()
    if not raw:
        return default
    return int(raw)


def _bool_env(key: str, default: bool = False) -> bool:
    raw = os.environ.get(key, "").strip().lower()
    if not raw:
        return default
    return raw in ("1", "true", "yes", "on")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-change-in-production")
DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() in ("1", "true", "yes")

_hosts = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")
ALLOWED_HOSTS = [h.strip() for h in _hosts.split(",") if h.strip()]

# Région par défaut pour numéros sans indicatif (ISO 3166-1 alpha-2), ex. CD = RDC.
PHONE_DEFAULT_REGION = os.environ.get("PHONE_DEFAULT_REGION", "CD").strip() or "CD"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    "drf_spectacular",
    "corsheaders",
    "users",
    "authentication",
    "inscription",
    "post",
    "messagerie",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
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

WSGI_APPLICATION = "config.wsgi.application"

# MySQL / MariaDB (même backend Django). Index utf8mb4, chemins fichiers 512 car., charset des DB de test : voir .env.example (WAMP / XAMPP).
_db_engine = os.environ.get("DB_ENGINE", "django.db.backends.mysql").strip()
_db_options: dict = {"charset": "utf8mb4"}
# Une seule instruction ; sur anciennes versions MySQL/MariaDB, définir DB_INIT_COMMAND vide pour désactiver.
_init_cmd = os.environ.get("DB_INIT_COMMAND", "SET sql_mode='STRICT_TRANS_TABLES'").strip()
if _init_cmd:
    _db_options["init_command"] = _init_cmd
_read_default = os.environ.get("DB_READ_DEFAULT_FILE", "").strip()
if _read_default:
    _db_options["read_default_file"] = _read_default

_default_db = {
    "ENGINE": _db_engine,
    "NAME": os.environ.get("DB_NAME", "bdd_unilukaapp").strip(),
    "USER": os.environ.get("DB_USER", "root").strip(),
    "PASSWORD": os.environ.get("DB_PASSWORD", ""),
    "HOST": os.environ.get("DB_HOST", "127.0.0.1").strip(),
    "PORT": os.environ.get("DB_PORT", "3306").strip(),
    "OPTIONS": _db_options,
    "CONN_MAX_AGE": _int_env("DB_CONN_MAX_AGE", 0),
    "CONN_HEALTH_CHECKS": _bool_env("DB_CONN_HEALTH_CHECKS", False),
}

# Bases de test MySQL/MariaDB : charset explicite (évite mélanges utf8 / utf8mb4 sous WAMP)
if _db_engine == "django.db.backends.mysql":
    _default_db["TEST"] = {
        "CHARSET": "utf8mb4",
        "COLLATION": "utf8mb4_unicode_ci",
    }

DATABASES = {"default": _default_db}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Africa/Kinshasa"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "config.pagination.StandardResultsSetPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "config.exceptions.custom_exception_handler",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=48),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "UPDATE_LAST_LOGIN": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# CORS : chaque entrée doit être une URL avec schéma (ex. http://localhost:3000).
# "*" ou "all" seuls dans CORS_ALLOWED_ORIGINS activent CORS_ALLOW_ALL_ORIGINS (django-cors n'accepte pas * dans la liste).
_cors_raw = os.environ.get("CORS_ALLOWED_ORIGINS", "").strip()
_cors_force_all = os.environ.get("CORS_ALLOW_ALL_ORIGINS", "").strip().lower() in (
    "1",
    "true",
    "yes",
    "on",
)

if _cors_force_all:
    CORS_ALLOW_ALL_ORIGINS = True
elif not _cors_raw:
    CORS_ALLOW_ALL_ORIGINS = DEBUG
else:
    _cors_parts = [o.strip() for o in _cors_raw.split(",") if o.strip()]
    _filtered = [p for p in _cors_parts if p.lower() not in ("*", "all")]
    if not _filtered:
        CORS_ALLOW_ALL_ORIGINS = True
    else:
        CORS_ALLOWED_ORIGINS = _filtered

SPECTACULAR_SETTINGS = {
    "TITLE": "API académique",
    "DESCRIPTION": (
        "Documentation groupée **par table** (opérations CRUD). "
        "Base URL des ressources : `/api/`."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "TAGS": [
        {"name": name, "description": TAG_DESCRIPTIONS.get(name, "")}
        for name in TAG_ORDER
    ],
    "POSTPROCESSING_HOOKS": ["config.schema.reorder_tags_hook"],
}

LOG_LEVEL = os.environ.get("DJANGO_LOG_LEVEL", "INFO")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
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
        "level": LOG_LEVEL,
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
}
