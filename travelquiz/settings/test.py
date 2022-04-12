from .base import *

DEBUG = True
ENVIRONMENT = 'TEST'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}

ENCRYPTOR_SECRET_KEY='aaaaaaaaaaaaaaaa'
