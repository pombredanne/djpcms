from djpcms import sites


if sites.settings.CMS_ORM == 'django':
    
    from django.db.models import *
        
elif sites.settings.CMS_ORM == 'stdnet':
    
    from stdnet.orm import *
    
    Model = StdModel
    TextField = CharField
    
else:
    
    from djpcms.core.db import *