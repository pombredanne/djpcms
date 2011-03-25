from djpcms_test_settings import *

CMS_ORM = 'stdnet'

INSTALLED_APPS  = ['stdnet.contrib.sessions',
                   'stdnet.contrib.tagging',
                   'djpcms']


MIDDLEWARE_CLASSES = (
    'stdnet.contrib.sessions.middleware.SessionMiddleware',
)