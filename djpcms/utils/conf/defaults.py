import djpcms

#######################################    GLOBAL FLAGS
DEBUG = False
SECRET_KEY = 'djpcms'   # Secret key, please change this to a unique value
PROFILING_KEY = None
TEMPLATE_ENGINE = None
DESCRIPTION = 'djpcms framework'
EPILOG = 'Have fun!'

#######################################    META ATTRIBUTE
META_TAGS = ('charset', 'robots', 'description',
             'keywords', 'author', 'viewport')
META_DESCRIPTION = ''
META_KEYWORDS = ''
META_AUTHOR = ''
META_VIEWPORT = 'width=device-width, initial-scale=1'
DEFAULT_CHARSET = 'utf-8'
TIME_ZONE = 'Europe/London'
LANGUAGE_CODE = 'en-uk'

# List of installed application.
# These must be dotted python paths
INSTALLED_APPS = ()
DATASTORE = {}
# Dictionary used to configure applications
INSTALLED_APPS_CONF = {}
APPLICATION_URLS = None
CACHE_VIEW_OBJECTS = True
DJPCMS_IMAGE_UPLOAD_FUNCTION = None
DJPCMS_EMPTY_VALUE = '(None)'
SITEMAP_TIMEOUT = 60
#
# To group applications admin together. Check the documentation
ADMIN_GROUPING = None

#MIDDLEWARE AND CONTEXT PROCESSORS
AUTHENTICATION_BACKENDS = ('sessions.backends.ModelBackend',)
REQUEST_CONTEXT_PROCESSORS = ()

TEMPLATE_DIRS = ()  # Additional template location directories
DEFAULT_TEMPLATE_NAME = 'default'
DEFAULT_INNER_TEMPLATE = 'djpcms/inner/cols2_66_33.html'
JS_START_END_PAGE = 101
EXTRA_CONTENT_PLUGIN = None

#######################################    CSS GRID LAYOUT
LAYOUT_GRID_SYSTEM = '960' # '960_16_float' for a 16 columns float layout

#######################################    NAVIGATION
SITE_NAVIGATION_LEVELS = 4
SITE_NAVIGATION_BRAND = None
ENABLE_BREADCRUMBS = 2

#######################################    PLUGINS
DJPCMS_PLUGINS = ['djpcms.plugins.*']
DJPCMS_WRAPPERS = ['djpcms.plugins.extrawrappers']


DJPCMS_SITE_MAP = True
DJPCMS_USER_CAN_EDIT_PAGES = False
# Date Format
DATE_FORMAT = 'd M Y'
TIME_FORMAT = 'H:i:s'


#######################################    JINJA2 Settings
#TEMPLATE_ENGINE = 'jinja2'
JINJA2_EXTENSIONS = []
JINJA2_TEMPLATE_LOADERS = (('djpcms.apps.jinja2template.ApplicationLoader',),)

#######################################    STATIC FILES
MEDIA_URL = '/media/'
FAVICON_MODULE = None
JQUERY_VERSION = '1.7.1'
JQUERY_UI_VERSION = '1.8.16'
SWFOBJECT_VERSION = '2.2'
BOOTSTRAP_VERSION = '1.4.0'
BOOTSTRAP_LIBS = ()
HTML = djpcms.HTML_CLASSES.copy()
DEFAULT_STYLE_SHEET = djpcms.DEFAULT_STYLE_SHEET()
DEFAULT_JAVASCRIPT = djpcms.DEFAULT_JAVASCRIPT()

#######################################    SPHINX CONFIG
SPHINX__extensions = ['sphinx.ext.pngmath',
                      'sphinx.ext.extlinks']

#######################################    LOGGING
LOGGING = djpcms.LOGGING_SAMPLE


#######################################    ANALYTICS
GOOGLE_ANALYTICS_ID = None
