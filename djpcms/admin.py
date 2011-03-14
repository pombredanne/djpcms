from djpcms.models import Page, InnerTemplate, BlockContent
from djpcms.apps.included.sitemap import SiteMapApplication

NAME = 'Layout'
ROUTE = 'layout'

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
                                   form = HtmlTemplateForm,
                                   list_display = ('id','name','numblocks'),
                                   object_display = ('id','name','numblocks','template'),
                                   list_display_links = ('name',)),
                  ContentSite('/blocks/',
                              BlockContent,
                              form = ContentBlockHtmlForm,
                              list_display = ('id','page','block','position',
                                              'plugin_name','title','requires_login'),
                              object_display = ('id','page','block','position',
                                              'plugin_name','title','requires_login',
                                              'for_not_authenticated'))
                  )

else:
    admin_urls = (
                  SiteMapApplication('/pages/',
                                     description = 'site map'),
                  )
