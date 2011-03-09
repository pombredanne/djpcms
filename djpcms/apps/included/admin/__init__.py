'''An application which displays a table with all applications
registered in the same ApplicationSite::

    from djpcms.apps.included.admin import SiteAdmin
    from djpcms.apps.included.sitemap import SiteMapView
    
    admin_urls = (
                  SiteAdmin('/', name = 'admin'),
                  SiteMapView('/sitemap/', name = 'sitemap'),
                 )
                  
'''
from .site import *