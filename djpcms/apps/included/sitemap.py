'''An application for displaying the sitemap as a table tree. To use add the
following to your application urls tuple::

    SiteMapApplication('/sitemap/', name = 'sitemap', in_navigation = 100)
'''
from djpcms import views, sites
from djpcms.template import loader
from djpcms.models import Page
from djpcms.utils import gen_unique_id
from djpcms.html import box, table

    
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
    
    

class PageChangeView(views.ChangeView):
            
    def get_context(self, djp):
        c = super(PageChangeView,self).get_context(djp)
        page = djp.instance
        cdjp = djp.site.djp(djp.request, page.url[1:])
        inner = c['inner']
        c['inner'] = box(collapsed = True, bd = inner, hd = 'Page properties')
        c['underlying'] = cdjp.view.get_context(cdjp, editing = True)['inner']
        return c     
        
    
class SiteMapApplication(views.ModelApplication):
    '''Application to use for admin sitemaps'''
    list_display = ('url','application','application_view',
                    'template','inner_template')
    main = SiteMapView(in_navigation = 1)
    
    if Page:
        add = views.AddView(parent = 'main', force_redirect = True)
        change = PageChangeView(regex = views.IDREGEX,
                                parent = 'main',
                                force_redirect = True,
                                template_name = 'djpcms/admin/editpage.html')
        delete = views.DeleteView(parent = 'change')
        
        def __init__(self, baseurl, **kwargs):
            super(SiteMapApplication,self).__init__(baseurl,Page,**kwargs)
    
    else:
        def __init__(self, baseurl, **kwargs):
            views.Application.__init__(self,baseurl,**kwargs)
            
    
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
              'djpcms/apps/sitemap.js')