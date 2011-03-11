from djpcms.models import Page, InnerTemplate, BlockContent
from djpcms.apps.included.sitemap import SiteMapApplication

if Page:
    from djpcms.apps.included.contentedit import ContentSite, HtmlPageForm, \
                                                 HtmlTemplateForm, ContentBlockHtmlForm 
    from djpcms.apps.included.admin import AdminApplication
    
    admin_urls = (
                  SiteMapApplication('/pages/',
                                     description = 'site map',
                                     form = HtmlPageForm),
                  AdminApplication('/templates/',
                                   InnerTemplate,
                                   description = 'inner templates',
                                   form = HtmlTemplateForm),
                  ContentSite('/blocks/',
                              BlockContent,
                              form = ContentBlockHtmlForm),
                  )

else:
    admin_urls = (
                  SiteMapApplication('/pages/',
                                     description = 'site map')
                  )
