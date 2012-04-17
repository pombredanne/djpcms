'''An application for displaying the sitemap as a table tree. To use add the
following to your application urls tuple::

    SiteMapApplication('/sitemap/',
                        name = 'sitemap')
'''
from djpcms import views, Http404
from djpcms.core import messages
from djpcms.html.layout import htmldoc, grid, container
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
    

def reder_edit_form(request):
    text = self.render(request)
    body = grid('grid 100')(self.render(request))
    body = body.render(request)
    underlying = request.underlying()
    edit = Widget('div', body, cn = 'edit-panel')
    context = underlying.get_context(editing = True)
    context['body'] = Widget('div',(edit,context['body'])).render(request)
    context['title'] = 'Edit ' + context['title']
    return context
    
    
class PageChangeView(views.ChangeView):
    name='change'
    edit_container=container('edit-page', renderer=reder_edit_form)
    '''Change page data'''
    
    def underlying(self, request):
        return underlying_response(request, request.instance)
        
    def get_context(self, request):
        page = request.instance
        layout = page.layout
        layout = self.root.get_page_layout(layout)()
        # Insert edit container
        edit_container = layout.maker.child_widget(self.edit_container,layout)
        children = OrderedDict({self.edit_container.key: edit_container})
        children.update(layout.children)
        layout.children = children
        return layout.render(request)
        
    def reder_edit_form(self, request):
        text = self.render(request)
        body = grid('grid 100')(self.render(request))
        body = body.render(request)
        underlying = request.underlying()
        edit = Widget('div', body, cn = 'edit-panel')
        context = underlying.get_context(editing = True)
        context['body'] = Widget('div',(edit,context['body'])).render(request)
        context['title'] = 'Edit ' + context['title']
        return context
    
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
    
    
class SiteMapApplication(TabViewMixin, views.Application):
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
        
    def instance_field_value(self, request, page, field_name, val = ''):
        if field_name == 'view':
            node = request.tree.get(page.url)
            view = node.view
            if not isinstance(view,views.pageview):
                return view.code
            else:
                return ''
        else:
            return val
    