from djpcms import sites


if sites.tests.CMS_ORM == 'django':
    
    from django.db.models import *
        
elif sites.tests.CMS_ORM == 'stdnet':
    
    from stdnet.orm import *
    
    Model = StdModel
    TextField = CharField


def user_and_session():
    if sites.tests.CMS_ORM == 'django':
        from django.conrib.auth.models import User
        from django.conrib.sessions.models import Session
    elif sites.tests.CMS_ORM == 'stdnet':
        from stdnet.conrib.sessions.models import User, Session
    else:
        User, Session = None, None
    
    return User, Session