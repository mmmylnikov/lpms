import json
from os import getenv
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SHARED_ROOT = BASE_DIR / 'shared'

SECRET_KEY = getenv('DJANGO_SECRET_KEY')

DEBUG = getenv("DEBUG", 'False').lower() in ('true', '1')


ALLOWED_HOSTS = getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1').split(',')

INSTALLED_APPS = [
    # LPMS
    'user.apps.UserConfig',
    'course.apps.CourseConfig',
    'learn.apps.LearnConfig',
    'dashboard.apps.DashboardConfig',
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
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
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = 'config.urls'

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
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

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

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

STATIC_ROOT = SHARED_ROOT / 'static'

STATICFILES_DIRS = [
    # SHARED_ROOT / "static",
    # "/var/www/static/",
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

INTERNAL_IPS = [
    "127.0.0.1",
]


# GitHub OAuth
REST_USE_JWT = True
SITE_ID = 1
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_EMAIL_VERIFICATION = "none"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
CALLBACK_URL_YOU_SET_ON_GITHUB = 'http://localhost:8002/oauth/callback'

SOCIALACCOUNT_PROVIDERS = {
    "github": {
        "APP": {
            "client_id": getenv('GITHUB_OAUTH_CLIENT_ID'),
            "secret": getenv('GITHUB_OAUTH_SECRET'),
            "redirect_uri": getenv('GITHUB_OAUTH_REDIRECT_URL'),
        }
    }
}

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

GITHUB_API_TOKEN = getenv('GITHUB_API_TOKEN')
