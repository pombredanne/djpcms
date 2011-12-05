import djpcms

DEBUG = False
SECRET_KEY = 'djpcms'   # Secret key, please change this to a unique value
PROFILING_KEY = None
DESCRIPTION = 'djpcms framework'
EPILOG = 'Have fun!'

# META ATTRIBUTE
META_DESCRIPTION = ''
META_KEYWORDS = ''
META_AUTHOR = ''
DEFAULT_CHARSET = 'utf-8'
TIME_ZONE = 'Europe/London'
LANGUAGE_CODE = 'en-uk'

# List of installed application.
# These must be dotted python paths
INSTALLED_APPS = ['djpcms']
DATASTORE = {}
# Dictionary used to configure applications
INSTALLED_APPS_CONF = {}
APPLICATION_URLS = None
MAX_SEARCH_DISPLAY = 20
CACHE_VIEW_OBJECTS = True
DJPCMS_IMAGE_UPLOAD_FUNCTION = None
DJPCMS_EMPTY_VALUE = '(None)'
SITEMAP_TIMEOUT = 60
#
# To group applications admin together. Check the documentation
ADMIN_GROUPING = None

#MIDDLEWARE AND TEMPLATE PROCESSORS
AUTHENTICATION_BACKENDS = ('sessions.backends.ModelBackend',)
REQUEST_CONTEXT_PROCESSORS = ("djpcms.core.context_processors.djpcms",
                              "djpcms.core.context_processors.messages")

TEMPLATE_DIRS = ()  # Additional template location directories
DEFAULT_TEMPLATE_NAME = ('base.html','djpcms/base.html')
DEFAULT_INNER_TEMPLATE = 'djpcms/inner/cols2_66_33.html'
DEFAULT_LAYOUT = 0 # 0 fixed, 1 float

# Root page for user account urls
USER_ACCOUNT_HOME_URL = '/accounts/'
JS_START_END_PAGE = 101
EXTRA_CONTENT_PLUGIN = None

# Analytics
GOOGLE_ANALYTICS_ID = None

SITE_NAVIGATION_LEVELS = 4
SITE_NAVIGATION_BRAND = None
ENABLE_BREADCRUMBS = 2

DJPCMS_PLUGINS = ['djpcms.plugins.*']
DJPCMS_WRAPPERS = ['djpcms.plugins.extrawrappers']
DJPCMS_SITE_MAP = True

DJPCMS_USER_CAN_EDIT_PAGES = False

# JINJA2 Settings
TEMPLATE_ENGINE = 'jinja2'
JINJA2_EXTENSIONS = []
JINJA2_TEMPLATE_LOADERS = (('djpcms.apps.jinja2template.ApplicationLoader',),)

# Date Format
DATE_FORMAT = 'd M y'
TIME_FORMAT = 'H:i:s'

# STATIC FILES
MEDIA_URL = '/media/'
FAVICON_MODULE = None
JQUERY_VERSION = '1.6.2'
JQUERY_UI_VERSION = '1.8.16'
SWFOBJECT_VERSION = '2.2'
DEFAULT_STYLE_SHEET = djpcms.DEFAULT_STYLE_SHEET()
DEFAULT_JAVASCRIPT = djpcms.DEFAULT_JAVASCRIPT()

#SPHINX CONFIG
SPHINX__extensions = ['sphinx.ext.pngmath',
                      'sphinx.ext.extlinks']

# Finally Logging
LOGGING = djpcms.LOGGING_SAMPLE

HTML = djpcms.HTML_CLASSES.copy()