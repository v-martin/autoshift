from autoshift.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

DEBUG = False

# Use a faster, but less secure secret key for testing
SECRET_KEY = 'django-insecure-test-key-for-testing-only'

# Turn off migrations for tests
MIGRATION_MODULES = {app.split('.')[-1]: None for app in INSTALLED_APPS if app.startswith('django.') is False}

# Make test output faster
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Set test-specific REST framework settings
REST_FRAMEWORK = {
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'TEST_REQUEST_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ]
}


