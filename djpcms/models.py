from djpcms import sites

if sites.settings.CMS_ORM == 'django':
    
    from djpcms.core.cmsmodels._django import *
    
elif sites.settings.CMS_ORM == 'stdnet':
    
    from djpcms.core.cmsmodels._stdnet import *
    
elif sites.settings.CMS_ORM == 'sqlalchemy':
    
    from djpcms.core.cmsmodels._sqlalchemy import *
    
else:
    BlockContent = None
    Page = None
    Site = None
    InnerTemplate = None

