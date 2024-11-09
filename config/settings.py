"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 5.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        # Приложения проекта
        'infoMFSS',
        'users',
        # Сторонние приложения из библиотек
        'sass_processor',
        'crispy_forms',
        'crispy_bootstrap5',
]

MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

TEMPLATES = [
        {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': [TEMPLATE_DIR, ],
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

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
DATABASES = {
        'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.getenv('POSTGRES_DB'),
                'USER': os.getenv('POSTGRES_USER'),
                'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
                'PORT': os.getenv('POSTGRES_PORT'),
                # 'HOST': os.getenv('POSTGRES_HOST'),
        }
}
# end

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# end

# Internationalization настройка
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True
# end

# Настройка статических файлов
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
# STATIC_URL = '/static/' # возможно придется сделать так

# STATIC_DIRS = os.path.join(BASE_DIR, 'static/') # это пока не нужно
# STATICFILES_DIRS = [(os.path.join(BASE_DIR, 'static'))] # это пока не нужно
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
SASS_PROCESSOR_ROOT = STATIC_ROOT

STATICFILES_FINDERS = [
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        'sass_processor.finders.CssFinder',
]

MEDIA_URL = 'media/'  # это пока не нужно
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # это пока не нужно
# end

# Настройка отправки сообщений по электронной почте
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 587
EMAIL_USE_SSL = True

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER
EMAIL_ADMIN = EMAIL_HOST_USER
# end

# Кэширование
CASH_ENABLE = os.getenv('CACHE_ENABLED') == '1'

if CASH_ENABLE:
    CACHES = {
            "default": {
                    "BACKEND": "django.core.cache.backends.redis.RedisCache",
                    "LOCATION": os.getenv("CACHE_LOCATION")
            }
    }
# end

# Защита от CSRF атак
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True
# CSRF_USE_SESSION_ID = False
# end

# Конфигурация CORS

CORS_ALLOWED_ORIGINS = ['http://127.0.0.1:8000', ]

CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000', ]

CORS_ALLOW_ALL_ORIGINS = False
# CORS_ALLOWED_ORIGINS = [
#         'http://localhost:8000',
#         'https://your-domain.com',
# ]

# CORS_ALLOW_ALL_ORIGINS = True
# CORS_ALLOW_CREDENTIALS = True
# CORS_EXPOSE_HEADERS = ['X-Custom-Header']
# CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'DELETE']
# CORS_PREFLIGHT_MAX_AGE = 86400
# CORS_REPLACE_HTTPS_REFERER = True
# end

# Конфигурация для Celery
# Установка в локальной среде
# CELERY_BROKER_URL = 'redis://localhost:6379'
# CELERY_RESULT_BACKEND = 'redis://localhost:6379'

# Установка при связи с docker и на продакшн
# CELERY_BROKER_URL = 'redis://redis:6379/0'
# CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
#
# CELERY_TIMEZONE = "Europe/Moscow"
# CELERY_TASK_TRACK_STARTED = True
# CELERY_TASK_TIME_LIMIT = 30 * 60
# CELERY_SCHEDULER = 'celery.schedulers.DatabaseScheduler'
# CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
# CELERY_ACCEPT_CONTENT = ['application/json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'
# end

# Конфигурация для Swagger
# SWAGGER_SETTINGS = {
#         'DEFAULT_API_VERSION': '1.0',
#         'DEFAULT_TITLE': 'API МФСС',
#         'DEFAULT_DESCRIPTION': 'API для работы с МФСС',
# }
# end

# Settings telegram
TELEGRAM_URL = 'https://api.telegram.org/bot'
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
USER_ID_TELEGRAM = os.getenv('USER_ID_TELEGRAM')
# end

# Настройка аутентификации
AUTH_USER_MODEL = 'users.User'
LOGOUT_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = 'users:login'
# end

# Настройка вывода формата времени
TIME_INPUT_FORMATS = [
        "%H:%M",  # '14:30'
]
# end

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"