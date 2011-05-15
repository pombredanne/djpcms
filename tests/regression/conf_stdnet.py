from djpcms_test_settings import *

CMS_ORM = 'stdnet'

INSTALLED_APPS  += ['djpcms.contrib.sessions',
                    'stdnet.contrib.searchengine']


MIDDLEWARE_CLASSES = (
    'djpcms.contrib.sessions.middleware.SessionMiddleware',
)