from djpcms.models import Page, InnerTemplate, BlockContent, SiteContent
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
                                     form = HtmlPageForm,
                                     list_display_links = ('url','inner_template')),
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
                              list_display_links = ('id','page'),
                              object_display = ('id','page','block','position',
                                              'plugin_name','title','requires_login',
                                              'for_not_authenticated')),
                  AdminApplication('/block-content/',
                                   SiteContent,
                                   description = 'site content',
                                   list_display = ('id','description','markup'),
                                   object_display = ('id','description','markup','body')
                  )
        )
else:
    admin_urls = (
                  SiteMapApplication('/pages/',
                                     description = 'site map'),
                  )
