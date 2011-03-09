from djpcms import sites


if sites.tests.CMS_ORM == 'django':
    
    from django.db.models import *
        
elif sites.tests.CMS_ORM == 'stdnet':
    
    from stdnet.orm import *
    
    Model = StdModel
    TextField = CharField
    