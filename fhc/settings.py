"""
Django settings for fhc — Foundation for Human Care NGO website.
"""

from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Environment / secrets -------------------------------------------------
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ["127.0.0.1", "localhost"]),
)
# Read .env if present (falls back to .env.example defaults during first run).
env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(env_file)

SECRET_KEY = env(
    "SECRET_KEY",
    default="django-insecure-dev-key-change-me-in-production-please",
)
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

# Domains allowed to submit forms over HTTPS (Django requires this in production).
# e.g. CSRF_TRUSTED_ORIGINS=https://affinix.cloud,https://www.affinix.cloud
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS", default=[])


# --- Applications ----------------------------------------------------------
INSTALLED_APPS = [
    # Themed admin (must come before django.contrib.admin)
    "jazzmin",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "crispy_forms",
    "crispy_bootstrap5",

    # Local apps
    "accounts",
    "core",
    "gallery",
    "programs",
    "blog",
    "events",
    "donations",
    "volunteers",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "fhc.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "fhc.wsgi.application"


# --- Database --------------------------------------------------------------
# Use PostgreSQL when DATABASE_URL is set (production), else SQLite (local dev).
# Example: DATABASE_URL=postgres://user:password@localhost:5432/fhc
if env("DATABASE_URL", default=""):
    DATABASES = {"default": env.db("DATABASE_URL")}
    DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# --- Authentication --------------------------------------------------------
AUTH_USER_MODEL = "accounts.User"
AUTHENTICATION_BACKENDS = [
    "accounts.backends.EmailBackend",
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "accounts:dashboard"
LOGOUT_REDIRECT_URL = "core:home"


# --- Internationalization --------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True


# --- Static & media --------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
# Use the hashed/compressed manifest storage only in production; the plain
# storage avoids needing `collectstatic` during local development.
_staticfiles_backend = (
    "django.contrib.staticfiles.storage.StaticFilesStorage"
    if DEBUG
    else "fhc.storage.ForgivingCompressedManifestStaticFilesStorage"
)
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": _staticfiles_backend},
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --- Crispy forms ----------------------------------------------------------
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"


# --- Email -----------------------------------------------------------------
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")

# Send real email once SMTP credentials are configured; otherwise print to the
# console so the flow can be tested without sending anything.
if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEFAULT_FROM_EMAIL = env(
    "DEFAULT_FROM_EMAIL",
    default="Foundation for Human Care <no-reply@fhc.org>",
)

# Where contact-form submissions are emailed.
CONTACT_NOTIFICATION_EMAIL = env(
    "CONTACT_NOTIFICATION_EMAIL", default="jallellavenky42@gmail.com"
)


# --- Razorpay --------------------------------------------------------------
RAZORPAY_KEY_ID = env("RAZORPAY_KEY_ID", default="")
RAZORPAY_KEY_SECRET = env("RAZORPAY_KEY_SECRET", default="")
RAZORPAY_WEBHOOK_SECRET = env("RAZORPAY_WEBHOOK_SECRET", default="")


# --- Jazzmin admin theme ---------------------------------------------------
JAZZMIN_SETTINGS = {
    "site_title": "FHC Admin",
    "site_header": "Foundation for Human Care",
    "site_brand": "Foundation for Human Care",
    "welcome_sign": "Welcome to the FHC admin portal",
    "copyright": "Foundation for Human Care",
    "search_model": ["accounts.User", "donations.Donation"],
    "topmenu_links": [
        {"name": "View Site", "url": "/", "new_window": True},
    ],
    "icons": {
        "accounts.User": "fas fa-user",
        "accounts.Profile": "fas fa-id-card",
        "gallery.Album": "fas fa-images",
        "gallery.Photo": "fas fa-image",
        "programs.Program": "fas fa-hand-holding-heart",
        "blog.Post": "fas fa-newspaper",
        "blog.Category": "fas fa-tags",
        "events.Event": "fas fa-calendar-day",
        "events.EventRegistration": "fas fa-ticket-alt",
        "donations.Donation": "fas fa-donate",
        "volunteers.Opportunity": "fas fa-people-carry",
        "volunteers.Application": "fas fa-file-signature",
        "core.NewsletterSubscriber": "fas fa-envelope",
        "core.ContactMessage": "fas fa-comment-dots",
        "core.SiteSetting": "fas fa-cog",
    },
    "order_with_respect_to": [
        "core", "programs", "donations", "volunteers",
        "events", "gallery", "blog", "accounts",
    ],
}
JAZZMIN_UI_TWEAKS = {
    "theme": "flatly",
    "navbar": "navbar-success navbar-dark",
    "sidebar": "sidebar-dark-success",
    "accent": "accent-success",
}


# --- Production security (active only when DEBUG is off) --------------------
if not DEBUG:
    # Trust the X-Forwarded-Proto header set by Nginx so Django knows it's HTTPS.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=2592000)  # 30 days
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"


# --- Logging ---------------------------------------------------------------
# Log to stdout/stderr; captured by Gunicorn/systemd journal in production.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "[{levelname}] {asctime} {name}: {message}", "style": "{"}
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"}
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.request": {"handlers": ["console"], "level": "ERROR", "propagate": False},
    },
}
