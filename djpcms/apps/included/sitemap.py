'''An application for displaying the sitemap as a table tree. To use add the
following to your application urls tuple::

    SiteMapApplication('/sitemap/', name = 'sitemap', in_navigation = 100)
'''
from djpcms import views, sites
from djpcms.template import loader
from djpcms.models import Page
from djpcms.core import messages
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
    '''Change page data'''
    def get_context(self, djp):
        c = super(PageChangeView,self).get_context(djp)
        page = djp.instance
        kwargs = dict(djp.request.GET.items())
        try:
            url = page.url % kwargs
        except KeyError as e:
            return c
        inner = c['inner']
        c['inner'] = box(collapsed = True, bd = inner,
                         hd = 'Page properties')
        try:
            cdjp = djp.site.djp(djp.request, url[1:])
        except Exception as e:
            messages.error(djp.request,
                           'This page has problems. The url is probably wrong')
            c['underlying'] = ''
        else:
            c['underlying'] = cdjp.view.get_context(cdjp, editing = True)['inner']
        return c     
        
    def defaultredirect(self, request, next = None, instance = None, **kwargs):
        if next:
            return next
        return super(PageChangeView,self).defaultredirect(request,
                                                          instance = instance,
                                                          **kwargs)
        
    
class SiteMapApplication(views.ModelApplication):
    '''Application to use for admin sitemaps'''
    list_display = ('id', 'url','application','application_view',
                    'template','inner_template','in_navigation','doc_type')
    main = SiteMapView(in_navigation = 1)
    
    if Page:
        search = views.SearchView(regex = 'pages',
                                  parent = 'main',
                                  title = lambda djp : 'pages')
        add = views.AddView(parent = 'main',
                            force_redirect = True)
        view = views.ViewView()
        change = PageChangeView(force_redirect = True,
                                template_name = 'djpcms/admin/editpage.html',
                                title = lambda djp: 'editing')
        delete = views.DeleteView()
        
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