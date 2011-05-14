import djpcms
DEBUG = False

# List of installed application.
# These must be dotted python paths
INSTALLED_APPS = ['djpcms']
DATASTORE = {}
# Dictionary used to configure applications
INSTALLED_APPS_CONF = {}
APPLICATION_URLS = None
HTML_CLASSES = None
MAX_SEARCH_DISPLAY = 20
CACHE_VIEW_OBJECTS = True
DJPCMS_IMAGE_UPLOAD_FUNCTION = None
DJPCMS_EMPTY_VALUE = '(None)'
#
# To group applications admin together. Check the documentation
ADMIN_GROUPING = None

MIDDLEWARE_CLASSES = ()
TEMPLATE_DIRS = ()
TEMPLATE_CONTEXT_PROCESSORS = ("djpcms.core.context_processors.djpcms",
                               "djpcms.core.context_processors.messages")

HTTP_LIBRARY = None             #'django' # django, werkzeug
CMS_ORM = None                  # django, stdnet
TEMPLATE_ENGINE = 'jinja2'      # django, jinja2

MEDIA_URL = '/media/'
DEFAULT_TEMPLATE_NAME = ('base.html','djpcms/base.html')
DEFAULT_INNER_TEMPLATE = 'djpcms/inner/cols2_66_33.html'
DEFAULT_LAYOUT = 0 # 0 fixed, 1 float

# django settings
DJANGO = False
ROOT_URLCONF = 'djpcms.apps.djangosite.defaults.urls' # default value for django
ADMIN_URL_PREFIX = '/admin/'

# Root page for user account urls
USER_ACCOUNT_HOME_URL           = '/accounts/'
JS_START_END_PAGE               = 101
EXTRA_CONTENT_PLUGIN            = None

# Analytics
GOOGLE_ANALYTICS_ID             = None
LLOOGG_ANALYTICS_ID             = None

SITE_NAVIGATION_LEVELS          = 4
ENABLE_BREADCRUMBS              = 2

DJPCMS_PLUGINS                  = ['djpcms.plugins.*']
DJPCMS_WRAPPERS                 = ['djpcms.plugins.extrawrappers']
DJPCMS_SITE_MAP                 = True

DJPCMS_USER_CAN_EDIT_PAGES      = False

#
JINJA2_TEMPLATE_LOADERS = [('djpcms.utils.jinja2loaders.ApplicationLoader',)]
JINJA2_EXTENSIONS = []

# Date Format
DATE_FORMAT = 'd M y'
DATETIME_FORMAT = DATE_FORMAT + ' H:i'

# Finally Logging
LOGGING = djpcms.LOGGING_SAMPLE