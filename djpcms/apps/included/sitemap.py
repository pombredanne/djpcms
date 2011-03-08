from djpcms import views, sites
from djpcms.template import loader
from djpcms.models import Page
from djpcms.utils import gen_unique_id

    
class SiteMapView(views.View):
    '''View to display Sitemap on a table-tree'''
    def render(self, djp):
        return loader.render('djpcms/components/sitemap.html',
                             {'url': djp.url,
                              'id': gen_unique_id()})
        
    def ajax__reload(self, djp):
        request = djp.request
        fields = self.appmodel.list_display
        return sites.tree.tojson(fields, refresh = True)        
    
    
class SiteMapApplication(views.Application):
    '''Application to use for admin sitemaps'''
    list_display = ('url','application','application_view',
                    'template','inner_template')
    main = SiteMapView(in_navigation = 1)
    
    if Page:
        add = views.AddView(parent = 'main')
        edit = views.AddView(regex = views.IDREGEX, parent = 'main')
    
    class Media:
        js = ('djpkit/djpkit.js',
              'djpkit/jquery.splitter.js',
              'jquery_mtree/mtree.js',
              'jquery_mtree/mtree.crrm.js',
              'jquery_mtree/mtree.ui.js',
              'jquery_mtree/mtree.table.js',
              'jquery_mtree/mtree.dnd.js',
              'jquery_mtree/mtree.contextmenu.js',
              'jquery_mtree/mtree.types.js',
              'djpcms/sitemap.js')