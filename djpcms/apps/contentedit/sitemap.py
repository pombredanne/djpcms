'''An application for displaying the sitemap as a table tree. To use add the
following to your application urls tuple::

    SiteMapApplication('/sitemap/',
                        name = 'sitemap')
'''
from pulsar.utils.html import escape, mark_safe

from djpcms import views, media
from djpcms.utils import markups
from djpcms.html import box, Pagination, table_header, Widget, htmldoc
from djpcms.html.layout import grid, container
from djpcms.cms import Http404, messages, pageview, permissions
from djpcms.cms.formutils import request_get_data
from djpcms.apps.nav import page_links
from djpcms.apps.admin import AdminApplication

from .layout import HtmlPageForm
from . import classes

__all__ = ['SiteMapApplication', 'SiteContentApp']


def underlying_response(request, page):
    urlargs = dict(request_get_data(request).items())
    if page:
        route = page.route
        try:
            url = route.url(**urlargs)
        except KeyError as e:
            url = route.path
        underlying = request.for_path(url, urlargs={})
        if is_async(underlying):
            return underlying.add_callback(
                                lambda r: _underlying_response(request, r))
        else:
            return _underlying_response(request, underlying)


def _underlying_response(request, underlying):
    if not underlying:
        messages.error(request,
            'This page has problems. Could not find matching view')
    underlying.page_editing = True
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
            r = request.for_path(view.path, cache=False)
            yield PageView(r)


class PageChangeView(views.ChangeView):
    '''View for editing a page. It insert an
:class:`djpcms.html.layout.container` at the top of the page with the
editing form.'''
    name='change'
    _media = media.Media(js=['djpcms/rearrange.js'])
    edit_container=container('edit-page',
                             cn=classes.edit,
                             grid_fixed=False,
                             context_request=lambda r: r,
                             renderer=lambda r,namespace,col,b: r.render())

    def underlying(self, request):
        return underlying_response(request, request.instance)

    def get_response(self, request):
        page = request.instance
        layout = page.layout
        layout = self.root.get_page_layout(layout)()
        # Insert edit page form container
        edit_container = layout.maker.child_widget(self.edit_container, layout)
        cls = layout.children.__class__
        children = cls({edit_container.key: edit_container})
        children.update(layout.children)
        layout.children = children
        return layout

    def render(self, request, block=None, **kwargs):
        text = super(PageChangeView,self).render(request, block=True)
        links = page_links(request)
        return box(hd='Editing page {0}'.format(request.instance),
                   bd=text, collapsed=True, edit_menu=links)\
                .addClass(classes.edit)

    def defaultredirect(self, request, next = None, instance = None, **kwargs):
        if next:
            return next
        return super(PageChangeView,self).defaultredirect(request,
                                                          instance = instance,
                                                          **kwargs)

    def media(self, request):
        return self._media


class SiteMapApplication(views.Application):
    '''Application to use for admin sitemaps'''
    has_plugins = False
    form = HtmlPageForm
    description = 'Site-map'
    pagination = Pagination(('url', 'view', 'layout',
                             'inner_template', 'in_navigation',
                             table_header('doc_type',attrname='doctype'),
                             'soft_root'),
                            bulk_actions = [views.bulk_delete])
    list_display_links = ('id', 'url', 'page')

    home = SiteMapView()
    pages = views.SearchView('pages/',
                             icon='th-list',
                             title=lambda r: 'Pages',
                             linkname=lambda r: 'pages')
    add = views.AddView(force_redirect=True, linkname=lambda r: 'add page')
    view = views.ViewView()
    change = PageChangeView(force_redirect=True,
                            title=lambda djp: 'editing',
                            linkname=lambda djp : 'edit page',
                            body_class='editable')
    delete = views.DeleteView()

    def on_bound(self):
        self.root.internals['Page'] = self.mapper

    def view_for_instance(self, request, instance):
        return self.views['change']

    def instance_field_value(self, request, page, field_name, val = ''):
        if field_name == 'view':
            node = request.tree.get(page.url)
            view = node.view
            if not isinstance(view, pageview):
                return view.code
            else:
                return ''
        else:
            return escape(val)


script_template = '''<script type='text/javascript'>
    (function() {
        function run_script() {
            %s
        }
        if ($('body').hasClass('djpcms-loaded')) {
            run_script();
        } else {
            $.bind('djpcms-loaded', run_script);
        }
    }());
</script>
'''
class SiteContentApp(AdminApplication):

    def on_bound(self):
        # Register the Page mapper with the roo internal dictionary
        self.root.internals['SiteContent'] = self.mapper

    def render_instance_default(self, request, instance, **kwargs):
        mkp = markups.get(instance.markup)
        text = instance.body
        if mkp:
            text = mkp(request, text)
        w = Widget('div', text, cn=classes.sitecontent)
        if instance.javascript:
            g = script_template % instance.javascript
            script = g.replace('\r\n','\n')
            if request.is_xhr:
                w.add(script)
            else:
                request.media.add(media.Media(js=[script]))
        return w.render(request)
