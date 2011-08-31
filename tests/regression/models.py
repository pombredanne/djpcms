from djpcms import sites


if sites.tests.CMS_ORM == 'django':
    
    from django.db.models import *
    
    from django.conrib.auth.models import User
    from django.conrib.sessions.models import Session
        
elif sites.tests.CMS_ORM == 'stdnet':
    
    from stdnet.orm import *
    
    from djpcms.contrib.sessions.models import User, Session
    
    Model = StdModel
    TextField = CharField

else:
    
    Model, User, Session = None, None, None
