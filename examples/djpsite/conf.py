#Main settings file. The site actually import settings.py which in turns it
#imports this file and specify the reserved settings below

INSTALLED_APPS = ('djpcms',
                  'style',
                  'stdcms',
                  'stdcms.cms',
                  'stdcms.monitor',
                  'stdcms.sessions',
                  'pulsardjp',
                  'djpsite')
ENABLE_BREADCRUMBS = 1,
FAVICON_MODULE = 'djpcms'
DEFAULT_STYLE_SHEET = {'all':[
'http://yui.yahooapis.com/2.9.0/build/reset-fonts-grids/reset-fonts-grids.css',
"djpsite/smooth.css"]}
LANGUAGE_CODE = 'en-gb'

DATASTORE = {'default':'redis://127.0.0.1:6379?db=5&prefix=djpcms:'}


# RESERVED SETTINGS
SECRET_KEY = None