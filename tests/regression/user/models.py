from djpcms import sites


if sites.settings.CMS_ORM == 'django':
    
    from django.contrib.auth.models import User
    
    installed_apps = ('django.contrib.auth',
                      'django.contrib.sessions')
    
elif sites.settings.CMS_ORM == 'stdnet':
    
    from stdnet.contrib.sessions.models import User
    
    installed_apps = ('stdnet.contrib.sessions',)
    
else:
    
    from djpcms.core.db import *