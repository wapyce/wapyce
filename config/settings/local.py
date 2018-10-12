"""
Django settings for wapyce project in development environment.
"""

# pylint: disable=wildcard-import, unused-wildcard-import
from .base import *

DEBUG = True

ALLOWED_HOSTS = []

SECRET_KEY = 'qe+umxbr6$u%8k@ftu=ga-js=n)b2_&=h2qav=#f5r$48d(wtu'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': get_env_variable('DATABASE_LOCAL_NAME'),
        'USER': get_env_variable('DATABASE_LOCAL_USER'),
        'PASSWORD': get_env_variable('DATABASE_LOCAL_PASSWORD'),
        'HOST': get_env_variable('DATABASE_LOCAL_HOST'),
        'PORT': get_env_variable('DATABASE_LOCAL_PORT')
    }
}