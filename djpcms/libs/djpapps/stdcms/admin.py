from djpcms import views
from djpcms.utils import markups, mark_safe
from djpcms.apps.admin import AdminApplication
from djpcms.apps.sitemap import SiteMapApplication
from djpcms.apps.contentedit import ContentSite, HtmlPageForm, \
                                    HtmlTemplateForm, ContentBlockHtmlForm, \
                                    HtmlEditContentForm

from .models import Page, InnerTemplate, BlockContent, SiteContent

NAME = 'CMS'
ROUTE = 'cms'

# If Content Management System is available, enable admin for it

class SiteContentApp(AdminApplication):
    inherit = True
    def render_object(self, djp):
        instance = djp.instance
        mkp = markups.get(instance.markup)
        text = instance.body
        if mkp:
            text = mkp['handler'](text)
        return mark_safe(text)

admin_urls = (
      SiteMapApplication('/sitemap/',
                         Page,
                         description = 'Site-map',
                         form = HtmlPageForm,
                         list_display_links = ('url','inner_template')),
      AdminApplication('/templates/',
                       InnerTemplate,
                       description = 'Inner templates',
                       form = HtmlTemplateForm,
                       list_display = ('id','name','numblocks'),
                       object_display = ('id','name','numblocks','template'),
                       list_display_links = ('name',)),
      ContentSite('/blocks/',
                  BlockContent,
                  form = ContentBlockHtmlForm,
                  list_display = ('id','page','block','position',
                                  'plugin_name','title',
                                  'layout','requires_login'),
                  list_display_links = ('id','page'),
                  object_display = ('id','page','block','position',
                                  'plugin_name','title',
                                  'layout','requires_login',
                                  'for_not_authenticated')),
      SiteContentApp('/block-content/',
                     SiteContent,
                     form = HtmlEditContentForm,
                     description = 'Site content',
                     list_display = ('id','title','markup')
      )
    )
