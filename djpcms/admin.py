from djpcms.models import Page, InnerTemplate
from djpcms.apps.included.sitemap import SiteMapApplication

if Page:
    from djpcms.apps.included.contentedit import HtmlPageForm, HtmlTemplateForm
    from djpcms.apps.included.admin import AdminApplication
    
    admin_urls = (
                  SiteMapApplication('/pages/',
                                     description = 'site map',
                                     form = HtmlPageForm),
                  AdminApplication('/templates/',
                                   InnerTemplate,
                                   description = 'inner templates',
                                   form = HtmlTemplateForm),
                  )

else:
    admin_urls = (
                  SiteMapApplication('/pages/',
                                     description = 'site map')
                  )