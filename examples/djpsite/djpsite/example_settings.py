import os
basedir = os.path.split(os.path.abspath(__file__))[0]

ADMINS = (
     ('Luca Sbardella', 'luca.sbardella@gmail.com'),
)

MANAGERS = ADMINS

# This is just a dummy one for you to be able to test
SECRET_KEY = 'vctw)*^2z!1fzie12zzdxf45)-rc(^7qvd(vabn&1&ogwehidr'

MIDDLEWARE_CLASSES = (
    'djpcms.contrib.sessions.middleware.SessionMiddleware',
)

INSTALLED_APPS = (
    'djpcms',
    'djpcms.contrib.admin',
    'djpcms.contrib.jdep',
    'djpcms.contrib.social',
    #'flowrepo',
    #'tagging',
)


# The settings changed by the application
#==========================================================
import os
basedir = os.path.split(os.path.abspath(__file__))[0]
APPLICATION_URL_MODULE = 'sitedjpcms.appurls'
TEMPLATE_DIRS = (os.path.join(basedir,'templates'),)
MEDIA_ROOT = os.path.join(basedir, 'media')
MEDIA_URL = '/media/'
DJPCMS_STYLE = 'green'
TEMPLATE_CONTEXT_PROCESSORS = (
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
            "djpcms.core.context_processors.djpcms"
            )
DJPCMS_PLUGINS = ['djpcms.plugins.*']
#DJPCMS_PLUGINS = ['djpcms.plugins.*',
#                  'flowrepo.cms.plugins']
DJPCMS_USER_CAN_EDIT_PAGES = True
SOCIAL_AUTH_CREATE_USERS = True
#=========================================================
FLOWREPO_STORAGE_IMAGE      = 'sitedjpcms.storage.SiteFileSystemStorage'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s | (p=%(process)s,t=%(thread)s) | %(levelname)s | %(name)s | %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    }
}
