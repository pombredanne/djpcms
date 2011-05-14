from djpcms_test_settings import *

CMS_ORM = 'django'

INSTALLED_APPS  += ['django.contrib.auth',
                    'django.contrib.sessions',
                    'django.contrib.contenttypes',
                    'tagging']


MIDDLEWARE_CLASSES = (
    #'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'djpcms.middleware.error.LoggingMiddleware',
)