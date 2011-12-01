'''An application for displaying the sitemap as a table tree. To use add the
following to your application urls tuple::

    SiteMapApplication('/sitemap/',
                        name = 'sitemap')
'''
from djpcms import views
from djpcms.core import messages
from djpcms.html import box, Pagination

from .admin import TabViewMixin
    

class SiteMapView(views.SearchView):
    pass
    

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
            c['underlying'] = cdjp.view.get_context(cdjp,
                                                    editing = True)['inner']
        return c     
        
    def defaultredirect(self, request, next = None, instance = None, **kwargs):
        if next:
            return next
        return super(PageChangeView,self).defaultredirect(request,
                                                          instance = instance,
                                                          **kwargs)
        
    
class SiteMapApplication(TabViewMixin,views.Application):
    has_plugins = False
    '''Application to use for admin sitemaps'''
    pagination = Pagination(('id', 'url','application','application_view',
                             'template','inner_template','in_navigation',
                             'doc_type','soft_root','route'))
    
    search = SiteMapView()
    
    add = views.AddView(force_redirect = True)
    view = views.ViewView()
    change = PageChangeView(force_redirect = True,
                            template_file = 'djpcms/admin/editpage.html',
                            title = lambda djp: 'editing')
    delete = views.DeleteView()
        
    def on_bound(self):
        self.root.internals['Page'] = self.mapper
    