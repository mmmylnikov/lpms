import json
from os import getenv
from pathlib import Path
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from dotenv import load_dotenv

load_dotenv(override=True)


sentry_sdk.init(
    dsn=getenv('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    auto_session_tracking=getenv("SENTRY_AUTO_SESSION_TRACKING", 'False').lower() in ('true', '1'),
    traces_sample_rate=float(getenv("SENTRY_TRACES_SAMPLE_RATE", '0.01')),
    release=getenv('RELEASE', 'unknown'),
    environment=getenv('SENTRY_ENVIRONMENT', 'dev'),
)


BASE_DIR = Path(__file__).resolve().parent.parent

SHARED_ROOT = BASE_DIR / 'shared'

SECRET_KEY = getenv('DJANGO_SECRET_KEY')

SITE_REPAIR = getenv("SITE_REPAIR", 'False').lower() in ('true', '1')

DEBUG = getenv("DEBUG", 'False').lower() in ('true', '1')

ALLOWED_HOSTS = getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1').split(',')

INTERNAL_IPS = getenv('INTERNAL_IPS', '').split(',')

CSRF_TRUSTED_ORIGINS = getenv('CSRF_TRUSTED_ORIGINS', '').split(',')

CORS_ALLOWED_ORIGINS = getenv('CORS_ALLOWED_ORIGINS', '').split(',')

INSTALLED_APPS = [
    # Admin interface
    'admin_interface',
    'colorfield',
    # LPMS
    'user.apps.UserConfig',
    'course.apps.CourseConfig',
    'learn.apps.LearnConfig',
    'dashboard.apps.DashboardConfig',
    'notify.apps.NotifyConfig',
    'backends',
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # pip install django-debug-toolbar
    "debug_toolbar",
    # pip install django-import-export
    'import_export',
    # pip install django-allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.github",
    # pip install django-dbbackup
    'dbbackup',
    'storages',
    # pip install django-extensions
    'django_extensions',
    # pip install django-cors-headers
    "corsheaders",
    # pip install django-health-check
    'health_check',
    'health_check.db',
    'health_check.cache',
    # 'health_check.storage',
    # 'health_check.contrib.s3boto3_storage',
    'health_check.contrib.migrations',
    'health_check.contrib.psutil',
]


HEALTH_CHECK = {
    'DISK_USAGE_MAX': int(getenv('HEALTH_CHECK_DISK_USAGE_MAX', '90')),
    'MEMORY_MIN': int(getenv('HEALTH_CHECK_MEMORY_MIN', '200')),
}

HEALTH_CHECK_TOKEN = getenv('HEALTH_CHECK_TOKEN', '')
HEALTH_CHECK_STATIC_FILE = getenv('HEALTH_CHECK_STATIC_FILE', 'healthcheck/test.txt')
HEALTH_CHECK_MEDIA_FILE = getenv('HEALTH_CHECK_MEDIA_FILE', 'healthcheck/test.txt')


# ROUTING

WSGI_APPLICATION = 'config.wsgi.application'

ROOT_URLCONF = 'config.urls'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'course.middleware.SuperuserDebugMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# DATABASE SETTINGS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.'
                  f'{getenv("DATABASE_ENGINE", "sqlite3")}',
        'NAME': getenv('DATABASE_NAME', 'lmpsdbdebug'),
        'USER': getenv('DATABASE_USERNAME', 'lpmsuserdebug'),
        'PASSWORD': getenv('DATABASE_PASSWORD', 'lpmspassdebug'),
        'HOST': getenv('DATABASE_HOST', '127.0.0.1'),
        'PORT': getenv('DATABASE_PORT', 5432),
        'OPTIONS': json.loads(getenv('DATABASE_OPTIONS', '{}')),
    }
}

if DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
    DATABASES['default']['NAME'] = SHARED_ROOT / 'db.sqlite3'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

TIME_ZONE = 'Europe/Moscow'

USE_TZ = True


# ADMIN THEME

X_FRAME_OPTIONS = "SAMEORIGIN"

SILENCED_SYSTEM_CHECKS = ["security.W019"]

LANGUAGE_CODE = 'ru-RU'

USE_I18N = True


# STORAGE SETTINGS

# DBBACKUP

DBBACKUP_DATE_FORMAT = getenv('DBBACKUP_DATE_FORMAT', '%Y%m%d_%H%M%S')

DBBACKUP_FILENAME_TEMPLATE = getenv('DBBACKUP_FILENAME_TEMPLATE', '{content_type}_{servername}_{databasename}_{datetime}.{extension}')

DBBACKUP_MEDIA_FILENAME_TEMPLATE = getenv('DBBACKUP_MEDIA_FILENAME_TEMPLATE', '{content_type}_{servername}_{databasename}_{datetime}.{extension}')

DBBACKUP_CONNECTORS = {
    'default': {
        'USER': getenv('DATABASE_USERNAME', 'lpmsuserdebug'),
        'PASSWORD': getenv('DATABASE_PASSWORD', 'lpmspassdebug'),
        'NAME': getenv('DATABASE_NAME', 'lmpsdbdebug'),
        'HOST': getenv('DATABASE_HOST', '127.0.0.1'),
        'PORT': getenv('DATABASE_PORT', 5432),
        'SINGLE_TRANSACTION': getenv("DBBACKUP_SINGLE_TRANSACTION", 'False').lower() in ('true', '1'),
        'CONNECTOR': getenv('DBBACKUP_CONNECTOR', 'dbbackup.db.postgresql.PgDumpBinaryConnector'),
    }
}

DBBACKUP_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

DBBACKUP_STORAGE_OPTIONS = {
    'access_key': getenv('STORAGE_DBBACKUP_access_key', 'access_key'),
    'secret_key': getenv('STORAGE_DBBACKUP_secret_key', 'secret_key'),
    'bucket_name': getenv('STORAGE_DBBACKUP_bucket_name', 'lmsdbbucket'),
    'default_acl': getenv('STORAGE_DBBACKUP_default_acl', 'private'),
    'region_name': getenv('STORAGE_DBBACKUP_region_name', 'nyc3'),
    'endpoint_url': getenv('STORAGE_DBBACKUP_endpoint_url', 'https://nyc3.digitaloceanspaces.com'),
    }


# STATIC SETTINGS

STORAGE_STATIC_BACKEND = getenv('STORAGE_STATIC_BACKEND', 's3').lower()

if STORAGE_STATIC_BACKEND == 's3':

    STATICFILES_STORAGE = 'backends.storages.PublicStaticStorage'

    STORAGE_STATIC_S3_CUSTOM_DOMAIN = getenv('STORAGE_STATIC_S3_CUSTOM_DOMAIN', None)

    STORAGE_STATIC_LOCATION = getenv('STORAGE_STATIC_LOCATION', 'static')

    STATIC_URL = f'{STORAGE_STATIC_S3_CUSTOM_DOMAIN}/{STORAGE_STATIC_LOCATION}/'

else:

    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

    STATIC_URL = 'static/'

STATIC_ROOT = SHARED_ROOT / 'static'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]


# MEDIA SETTINGS

STORAGE_MEDIA_BACKEND = getenv('STORAGE_MEDIA_BACKEND', 's3').lower()

if STORAGE_MEDIA_BACKEND == 's3':

    DEFAULT_FILE_STORAGE = 'backends.storages.PublicMediaStorage'

    STORAGE_MEDIA_S3_CUSTOM_DOMAIN = getenv('STORAGE_MEDIA_S3_CUSTOM_DOMAIN', None)

    STORAGE_MEDIA_LOCATION = getenv('STORAGE_MEDIA_LOCATION', 'media')

    MEDIA_URL = f'{STORAGE_MEDIA_S3_CUSTOM_DOMAIN}/{STORAGE_MEDIA_LOCATION}/'

else:

    MEDIA_URL = 'media/'

MEDIA_ROOT = SHARED_ROOT / 'media'


# USERS AUTH

AUTH_USER_MODEL = "user.User"

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

REST_USE_JWT = True

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_EMAIL_REQUIRED = True

ACCOUNT_EMAIL_VERIFICATION = "none"

LOGIN_REDIRECT_URL = "/"

LOGOUT_REDIRECT_URL = "/"

CALLBACK_URL_YOU_SET_ON_GITHUB = 'http://localhost:8000/oauth/callback'

# GitHub OAuth settings

SOCIALACCOUNT_PROVIDERS = {
    "github": {
        "APP": {
            "client_id": getenv('GITHUB_OAUTH_CLIENT_ID'),
            "secret": getenv('GITHUB_OAUTH_SECRET'),
            "redirect_uri": getenv('GITHUB_OAUTH_REDIRECT_URL'),
        }
    }
}


# Github API for learning processes

GITHUB_API_TOKEN = getenv('GITHUB_API_TOKEN')


# USERS NOTIFICATIONS

# Telegram Bot API for users notification

TELEGRAM_BOT_TOKEN = getenv('TELEGRAM_BOT_TOKEN')

TELEGRAM_BOT_USERNAME = getenv('TELEGRAM_BOT_USERNAME')


# Email settings for notifications about forgot password

EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"

EMAIL_FILE_PATH = SHARED_ROOT / "emails/app-messages"
