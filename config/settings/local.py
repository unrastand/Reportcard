from .base import *
from .base import env


DEBUG = True

# Disable external services for simplicity
USE_PAYMENT_OPTIONS = False
USE_SENTRY = False
USE_MAILCHIMP = False
USE_CELERY_REDIS = False

# Simple allowed hosts for development
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

THIRD_PARTY_APPS += [
    'debug_toolbar',
]
INSTALLED_APPS = DEFAULT_APPS + LOCAL_APPS + THIRD_PARTY_APPS

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Django-Debug-Toolbar
INTERNAL_IPS = ['127.0.0.1', 'localhost']
