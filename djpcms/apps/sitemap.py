'''An application for displaying the sitemap as a table tree. To use add the
following to your application urls tuple::

    SiteMapApplication('/sitemap/',
                        name = 'sitemap')
'''
from djpcms import views, Route, Http404
from djpcms.core import messages
from djpcms.core.layout import htmldoc
from djpcms.html import box, Pagination, table_header, Widget

from .admin import TabViewMixin
    

class SiteMapView(views.SearchView):
    pass
    

class PageChangeView(views.ChangeView):
    '''Change page data'''
    def get_context(self, request):
        ctx = super(PageChangeView,self).get_context(request)
        page = request.instance
        urlargs = dict(request.GET.items())
        route = Route(page.url)
        try:
            url = route.url(**urlargs)
        except KeyError as e:
            messages.error(request,
                    'This page has problems. The url is probably wrong')
            return ctx
        grid = request.cssgrid()
        prop = box(bd = ctx['inner'], hd = 'Page properties', cn = 'edit-block')
        sep = Widget('h2','Page layout',
                     cn='ui-state-default ui-corner-all edit-block')\
                    .css({'padding':'7px 14px'})
        inner = Widget('div',(prop,sep))
        container = Widget('div', inner)
        if grid:
            inner.addClass(grid.column1)
            container.add(grid.clear)
        underlying = request.for_url(url)
        if not underlying:
            messages.error(request,
                           'This page has problems. The url is probably wrong')
        else:
            container.add(underlying.get_context(editing = True)['inner'])
        ctx['inner'] = container.render(request)
        return ctx
        
    def defaultredirect(self, request, next = None, instance = None, **kwargs):
        if next:
            return next
        return super(PageChangeView,self).defaultredirect(request,
                                                          instance = instance,
                                                          **kwargs)
        

class PageView(object):
    
    def __init__(self, r):
        view = r.view
        page = r.page
        self.request = r
        self.view = view.code if view else None
        self.path = view.path
        self.in_navigation = r.in_navigation
        self.page = page
        self.id = page.id if page else None
        self.inner_template = page.inner_template if page else None
        self.doc_type = htmldoc(None if not page else page.doctype)
    
    
class SiteMapApplication(TabViewMixin,views.Application):
    has_plugins = False
    '''Application to use for admin sitemaps'''
    pagination = Pagination(('path','view','page','template',
                             'inner_template', 'in_navigation',
                             'doc_type', 'soft_root'),
                            bulk_actions = [views.bulk_delete])
    list_display_links = ('page','inner_template')
    
    search = SiteMapView()
    
    add = views.AddView(force_redirect = True,
                        linkname = lambda r : 'add page')
    view = views.ViewView()
    change = PageChangeView(force_redirect = True,
                            title = lambda djp: 'editing',
                            linkname = lambda djp : 'edit page')
    delete = views.DeleteView()
        
    def on_bound(self):
        self.root.internals['Page'] = self.mapper
                     
    def query(self, request, **kwargs):
        for view in request.view.root.all_views():
            r = request.for_view(view)
            yield PageView(r)
        
    