import djpcms

DEBUG = False
PROFILING_KEY = None
DESCRIPTION = 'DYNAMIC CONTENT MANAGEMENT SYSTEM FOR PYTHON AND JQUERY'
EPILOG = 'HAVE FUN!'


#######################################    APPLICATIONS
INSTALLED_APPS = () # These must be dotted python paths
DATASTORE = {}
# Dictionary used to configure applications
INSTALLED_APPS_CONF = {}

#######################################    META ATTRIBUTE
META_TAGS = ('charset', 'robots', 'description',
             'keywords', 'author', 'viewport')
META_DESCRIPTION = ''
META_KEYWORDS = ''
META_AUTHOR = ''
META_VIEWPORT = 'width=device-width, initial-scale=1'
DEFAULT_CONTENT_TYPE = 'text/html'
DEFAULT_CHARSET = 'utf-8'
TIME_ZONE = 'Europe/London'
LANGUAGE_CODE = 'en-uk'

CACHE_VIEW_OBJECTS = True
DJPCMS_IMAGE_UPLOAD_FUNCTION = None
DJPCMS_EMPTY_VALUE = '(None)'
SITEMAP_TIMEOUT = 60
#
# To group applications admin together. Check the documentation
ADMIN_GROUPING = None

###################################### MIDDLEWARE AND AUTHENTICATION
REQUEST_CONTEXT_PROCESSORS = ()
AUTHENTICATION_BACKENDS = ('sessions.backends.ModelBackend',)

TEMPLATE_DIRS = ()  # Additional template location directories
DEFAULT_TEMPLATE_NAME = 'default'
JS_START_END_PAGE = 101

#######################################    PLUGINS
DJPCMS_PLUGINS = ['djpcms.cms.plugins.*']
DJPCMS_WRAPPERS = ['djpcms.cms.plugins.extrawrappers']


DJPCMS_SITE_MAP = True
DJPCMS_USER_CAN_EDIT_PAGES = False
# Date Format
DATE_FORMAT = 'd M Y'
TIME_FORMAT = 'H:i:s'


#######################################    CSS AND JAVASCRIPT FILES
STYLING = 'smooth'
LAYOUT_GRID_SYSTEM = 'fixed_12'
MEDIA_URL = '/media/'
FAVICON_MODULE = None
JQUERY_VERSION = '1.7.2'
JQUERY_UI_VERSION = '1.8.21'
SWFOBJECT_VERSION = '2.2'
BOOTSTRAP_VERSION = '1.4.0'
BOOTSTRAP_LIBS = ()
DEFAULT_STYLE_SHEET = {}
DEFAULT_JAVASCRIPT = djpcms.DEFAULT_JAVASCRIPT()


#######################################    SPHINX CONFIG
SPHINX__extensions = ['sphinx.ext.pngmath',
                      'sphinx.ext.extlinks']


#######################################    LOGGING
LOGGING = djpcms.LOGGING_SAMPLE


#######################################    ANALYTICS
GOOGLE_ANALYTICS_ID = None


#######################################    CONNECTIONS
HTTP_PROXY = None
HTTPS_PROXY = None
