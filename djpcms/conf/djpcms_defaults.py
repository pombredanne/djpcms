import logging

DEBUG = False
# List of installed application. These must be dotted python paths
INSTALLED_APPS = ['djpcms']
DATASTORE = {}
# Dictionary used to configure applications
INSTALLED_APPS_CONF = {}
APPLICATION_URLS = None
LANGUAGE_REDIRECT               = False
HTML_CLASSES                    = None
MAX_SEARCH_DISPLAY              = 20
CACHE_VIEW_OBJECTS              = True
DJPCMS_IMAGE_UPLOAD_FUNCTION    = None
DJPCMS_EMPTY_VALUE              = '(None)'

SITE_ID = 1
MIDDLEWARE_CLASSES = ()
TEMPLATE_DIRS = ()
TEMPLATE_CONTEXT_PROCESSORS = ("djpcms.core.context_processors.djpcms",
                               "djpcms.core.context_processors.messages")

HTTP_LIBRARY = 'django' # django, werkzeug
CMS_ORM = None # django, stdnet
TEMPLATE_ENGINE = 'jinja2' # django, jinja2

MEDIA_URL = '/media/'
DEFAULT_TEMPLATE_NAME = ('base.html','djpcms/base.html')
DEFAULT_INNER_TEMPLATE = 'djpcms/inner/cols2_66_33.html'

# django settings
ROOT_URLCONF                    = 'djpcms.apps.djangosite.defaults.urls' # default value for django
ADMIN_URL_PREFIX                = '/admin/'
ADMIN_MEDIA_PREFIX              = '/media/admin/'

#Logging
GLOBAL_LOG_LEVEL                = logging.INFO
GLOBAL_LOG_FORMAT               = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
GLOBAL_LOG_HANDLERS             = [logging.StreamHandler()]

# Root page for user account urls
USER_ACCOUNT_HOME_URL           = '/accounts/'
JS_START_END_PAGE               = 101
EXTRA_CONTENT_PLUGIN            = None

# Analytics
GOOGLE_ANALYTICS_ID             = None
LLOOGG_ANALYTICS_ID             = None

SITE_NAVIGATION_LEVELS          = 2
ENABLE_BREADCRUMBS              = 2

DJPCMS_PLUGINS                  = ['djpcms.plugins.*']
DJPCMS_WRAPPERS                 = ['djpcms.plugins.extrawrappers']
DJPCMS_SITE_MAP                 = True

DJPCMS_USER_CAN_EDIT_PAGES      = False

#
JINJA2_TEMPLATE_LOADERS = [('djpcms.utils.jinja2loaders.ApplicationLoader',)]
JINJA2_EXTENSIONS = []

DJANGO = False
LOGGING_CONFIG = None
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s | (p=%(process)s,t=%(thread)s) | %(levelname)s | %(name)s | %(message)s'
        },
        'simple': {
            'format': '%(asctime)s %(levelname)s %(message)s'
        },
    },
    'handlers': {
        'silent': {
            'class': 'djpcms.utils.log.NullHandler',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'djpcms.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request':{
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}