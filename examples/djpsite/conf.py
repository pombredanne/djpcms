#Main settings file. The site actually import settings.py which in turns it
#imports this file and specify the reserved settings below

#STYLING = 'green'
INSTALLED_APPS = ('djpcms',
                  'stdcms',
                  'stdcms.cms',
                  'stdcms.monitor',
                  'stdcms.sessions',
                  'stdcms.social',
                  #
                  'djpcms.apps.fontawesome',
                  'djpcms.apps.nav',
                  'djpcms.apps.page',
                  'djpcms.apps.ui',
                  'djpcms.apps.color',
                  'djpcms.apps.contentedit',
                  #
                  'djpsite.apps.design',
                  'djpsite.apps.jstests',
                  'djpsite')
LANGUAGE_CODE = 'en-gb'
SITE_NAVIGATION_BRAND =\
"<img src='/media/djpsite/logos/djpcms-light-125x40.png' alt='djpcms'>"
DJPCMS_PLUGINS = ['djpcms.cms.plugins.*',
                  'djpcms.apps.contentedit.plugins']

DOMAIN_NAME = 'http://djpcms.com'


# RESERVED SETTINGS. CREATE A SETTINGS FILES AND OVERRIDE THESE VALUES
SECRET_KEY = 'dummy'
SESSION_COOKIE_NAME = 'djpsite-session'

GEOUSERNAME = ''
