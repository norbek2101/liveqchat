"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 4.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
from dotenv import dotenv_values
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from datetime import timedelta
import os


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


ENV = dotenv_values(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-vt3zdqaos(oggsqm4f2z*s7_047rmigf3m^ymut4lek7*@wwpa'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # my apps
    'bot',
    'accounts',
    'liveqchat',
    'api',

    # installed apps
    'rest_framework',
    'drf_yasg',
    'debug_toolbar',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'django.contrib.sites',
    'django_filters', 
    'corsheaders',
    'channels',
]

CORS_ALLOWED_ORIGINS = [
    'http://localhost:8080'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',    
    'corsheaders.middleware.CorsMiddleware',
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.Operators'

BOT_TOKEN = ENV['BOT_TOKEN']

NGROK_AUTHTOKEN = ENV['NGROK_AUTHTOKEN']

BASE_URL = None

BOTS = {}


REST_USE_JWT = True
SITE_ID = 1

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'api.paginations.CustomPagination',

    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend'
    ),

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'dj_rest_auth.jwt_auth.JWTCookieAuthentication',
    ),

    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),

    'DATETIME_FORMAT': "%Y-%m-%d %H:%M:%S",
}


SWAGGER_SETTINGS = {
    "USE_SESSION_AUTH": False,
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'in': 'header',
            'name': 'Authorization',
            'type': 'apiKey',
        },
    }
}


SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
JWT_AUTH_COOKIE = 'my-app-auth'
JWT_AUTH_REFRESH_COOKIE = 'my-refresh-token'

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_PASSWORD = ENV['EMAIL_HOST_PASSWORD']
EMAIL_HOST_USER = ENV['EMAIL_HOST_USER']


gettext = lambda s: s
LANGUAGES = (
    ('en', gettext('English')),
    ('ru', gettext('Russian')),
)



sentry_sdk.init(
    dsn="https://2526ca19305a494fbe10ad6675a249fa@o1279355.ingest.sentry.io/6479977",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True
)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'default': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
    },
    'handlers': {
        'main_debug': {
            'class': 'logging.FileHandler',
            'filename': f'{BASE_DIR}/logs/django/debug.log',
            'formatter': 'default',
        },
        'socket': {
            'class': 'logging.FileHandler',
            'filename': f'{BASE_DIR}/logs/daphne/debug.log',
            'formatter': 'default',
        },
        'other': {
            'class': 'logging.FileHandler',
            'filename': f'{BASE_DIR}/logs/others/warning.log',
            'formatter': 'default',
        },
        'printing': {
            'class': 'logging.FileHandler',
            'filename': f'{BASE_DIR}/logs/others/printing.log',
            'formatter': 'default',
        },
            'bot': {
                'class': 'logging.FileHandler',
                'filename': f'{BASE_DIR}/logs/bot/debug.log',
                'formatter': 'default',
            },
        # 'slave_bot': {
        #     'class': 'logging.FileHandler',
        #     'filename': f'{BASE_DIR}/clients/logs/slave_bot/debug.log',
        #     'formatter': 'default',
        # }
        # 'telegram': {
        #     'class': 'python_telegram_logger.Handler',
        #     'token': '5142838675:AAFiLX7xVFKyDFYqVpvRMN3Q_wIndc7T20w',
        #     'chat_ids': ['5142838675','632179390'],
        #     'filename': f'{BASE_DIR}/logs/bot/debug.log',
        #     "formatter": "default"
        # #     
        
        # },
    },
    'loggers': {
        'django': {
            'handlers': ['main_debug'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'daphne': {
            'handlers': ['socket'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.printing.messages': {
            'handlers': ['printing'],
        },
        'bot.asosiy': {
            'handlers': ['bot'],
            'level': 'INFO',
            'propagate': True,
        },
        # 'bot.slave': {
        #     'level': 'INFO',
        #     'handlers': ['slave_bot'],
        #     'propagate': True,
        # },
        # '': {
        #     'level': 'INFO',
        #     'handlers': ['other'],
        # },
        # 'tg': {
        #     'level': 'INFO',
        #     'handlers': ['telegram',],
        #     'propagate': True,
        # },
    },
}
