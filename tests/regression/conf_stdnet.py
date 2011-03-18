from djpcms_test_settings import *

CMS_ORM = 'stdnet'

INSTALLED_APPS  = ['stdnet.contrib.sessions',
                   'djpcms']


MIDDLEWARE_CLASSES = (
    'stdnet.contrib.sessions.middleware.SessionMiddleware',
)