'''An application for displaying the sitemap as a table tree. To use add the
following to your application urls tuple::

    SiteMapApplication('/sitemap/',
                        name = 'sitemap')
'''
from djpcms import views, Http404
from djpcms.core import messages
from djpcms.core.layout import htmldoc
from djpcms.forms.utils import request_get_data
from djpcms.html import box, Pagination, table_header, Widget

from .admin import TabViewMixin


def underlying_response(request, page):
    urlargs = dict(request_get_data(request).items())
    route = page.route
    try:
        url = route.url(**urlargs)
    except KeyError as e:
        messages.error(request,
            'Could not build for page. The url is probably wrong')
    else:
        underlying = request.for_path(url)
        if not underlying:
            messages.error(request,
                'This page has problems. Could not find matching view')
        return underlying


class PageView(object):
    
    def __init__(self, r):
        view = r.view
        page = r.page
        self.request = r
        self.view = view.code if view else None
        self.url = view.path
        self.in_navigation = r.in_navigation
        self.page = page
        self.id = page.id if page else None
        self.inner_template = page.inner_template if page else None
        self.doc_type = htmldoc(None if not page else page.doctype)
    

class SiteMapView(views.SearchView):
    pagination = Pagination(('url','view','page','template',
                             'inner_template', 'in_navigation',
                             'doc_type','soft_root'),
                            ajax = False)
    def query(self, request, **kwargs):
        for view in request.view.root.all_views():
            r = request.for_path(view.path, cache = False)
            yield PageView(r)
    

class PageChangeView(views.ChangeView):
    name = 'change'
    '''Change page data'''
    
    def underlying(self, request):
        return underlying_response(request, request.instance)
        
    def get_context(self, request):
        ctx = super(PageChangeView,self).get_context(request)
        underlying = request.underlying()
        if not underlying:
            return ctx
        page = request.instance
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
        container.add(underlying.get_context(editing = True)['inner'])
        ctx['inner'] = container.render(underlying)
        return ctx
    
    def cssgrid(self, request):
        underlying = request.underlying()
        if underlying is not None:
            return underlying.cssgrid()
        else:
            return super(PageChangeView,self).cssgrid(request)
        
    def defaultredirect(self, request, next = None, instance = None, **kwargs):
        if next:
            return next
        return super(PageChangeView,self).defaultredirect(request,
                                                          instance = instance,
                                                          **kwargs)
    
    
class SiteMapApplication(TabViewMixin,views.Application):
    has_plugins = False
    '''Application to use for admin sitemaps'''
    pagination = Pagination(('url','view','template',
                             'inner_template', 'in_navigation',
                             table_header('doc_type',attrname='doctype'),
                             'soft_root'),
                            bulk_actions = [views.bulk_delete])
    list_display_links = ('url','page','inner_template')
    
    home = SiteMapView()
    pages = views.SearchView('pages/',
                             title = lambda r : 'Pages',
                             linkname = lambda r : 'pages')
    add = views.AddView(force_redirect = True,
                        linkname = lambda r : 'add page')
    view = views.ViewView()
    change = PageChangeView(force_redirect = True,
                            title = lambda djp: 'editing',
                            linkname = lambda djp : 'edit page',
                            body_class = 'editable')
    delete = views.DeleteView()
        
    def on_bound(self):
        self.root.internals['Page'] = self.mapper
        
    def object_field_value(self, request, page, field_name, val = ''):
        if field_name == 'view':
            node = request.tree.get(page.url)
            view = node.view
            if not isinstance(view,views.pageview):
                return view.code
            else:
                return ''
        else:
            return val
    