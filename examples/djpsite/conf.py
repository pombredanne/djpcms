#Main settings file. The site actually import settings.py which in turns it
#imports this file and specify the reserved settings below

INSTALLED_APPS = ('djpcms',
                  'djpcms.style.plugins',
                  'style',
                  'stdcms.cms',
                  'stdcms.monitor',
                  'stdcms.sessions',
                  #'pulsardjp',
                  'djpsite')
ENABLE_BREADCRUMBS = 1
DEFAULT_STYLE_SHEET = {'all':[
'http://yui.yahooapis.com/2.9.0/build/reset-fonts-grids/reset-fonts-grids.css',
"djpsite/smooth.css"]}
LANGUAGE_CODE = 'en-gb'

# RESERVED SETTINGS. CREATE A SETTINGS FILES AND OVERRIDE THESE VALUES
SECRET_KEY = 'dummy'