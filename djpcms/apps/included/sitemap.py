'''An application for displaying the sitemap as a table tree. To use add the
following to your application urls tuple::

    SiteMapApplication('/sitemap/',
                        name = 'sitemap')
'''
from djpcms import views, sites
from djpcms.template import loader
from djpcms.models import Page
from djpcms.core import messages
from djpcms.html import box, table

from jslib.jquery_mtree.mixins import MtreeMixin, MtreeView
    
    
class SiteMapView(views.View, MtreeView):
    
    def render(self, djp):
        return self.appmodel.render_tree(djp)
        
    def get_root_tree(self, djp):
        return djp.tree
    

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
        
    
class SiteMapApplication(views.ModelApplication, MtreeMixin):
    '''Application to use for admin sitemaps'''
    list_display = ('id', 'url','application','application_view',
                    'template','inner_template','in_navigation','doc_type',
                    'soft_root','route')
    
    fields = ('path', 'id', 'application','application_view',
              'template','inner_template','in_navigation','doc_type',
              'title','linkname','is_soft','route')
    table_views = [
             {'name':'default',
              'fields': ('id','application','in_navigation','is_soft','doc_type')},
             {'name':'titles',
              'fields': ('id','route','title','linkname')}
             ]
    
    mtree = {
             'plugins': ('core','json','crrm','ui','table','types'),
             'table': {'min_height': '500px', 'name': 'path'}
             }
    
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
        js = MtreeMixin.MTREE_JAVASCRIPT
    