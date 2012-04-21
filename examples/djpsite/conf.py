#Main settings file. The site actually import settings.py which in turns it
#imports this file and specify the reserved settings below

INSTALLED_APPS = ('djpcms',
                  'stdcms',
                  'stdcms.cms',
                  'stdcms.monitor',
                  'stdcms.sessions',
                  'social',
                  #
                  # styling plugins
                  'djpcms.style.plugins.base',
                  'djpcms.style.plugins.fontawesome',
                  'djpcms.style.plugins.nav',
                  'djpcms.style.plugins.page',
                  'djpcms.style.plugins.table',
                  'djpcms.style.plugins.ui',
                  'djpcms.style.plugins.color',
                  #
                  #'pulsardjp',
                  'djpsite.apps.design',
                  'djpsite')
ENABLE_BREADCRUMBS = 1
DEFAULT_STYLE_SHEET = {'all':["djpsite/smooth.css"]}
LANGUAGE_CODE = 'en-gb'
SITE_NAVIGATION_BRAND =\
"<img src='/media/djpsite/logos/djpcms-light-125x40.png' alt='djpcms'>"
DJPCMS_PLUGINS = ['djpcms.plugins.*',
                  'djpcms.apps.contentedit.plugins']


# RESERVED SETTINGS. CREATE A SETTINGS FILES AND OVERRIDE THESE VALUES
SECRET_KEY = 'dummy'
SESSION_COOKIE_NAME = 'djpsite-session'