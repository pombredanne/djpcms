import logging
from copy import copy

from djpcms import Renderer, forms, media, ajax
from djpcms.utils.httpurl import range
from djpcms.utils.text import nicename, slugify, escape, UnicodeMixin

from .routing import Route
from .permissions import VIEW
from .formutils import submit_form

__all__ = ['RouteMixin', 'ViewRenderer', 'RendererMixin', 'ViewHandler',
           'pageview', 'SPLITTER']

SPLITTER = '-'

def makename(self, name, description):
    name = name or self.name
    if not name:
        path = self.path
        if '<' not in path:
            name = path.replace('/',' ')
        else:
            name = self.__class__.__name__.lower()
            if len(name) > 4 and name.endswith('view'):
                name = name[:-4]
    name = name.replace(SPLITTER,'_').lower()
    self.description = description or self.description or nicename(name)
    self.name = str(slugify(name,rtx='_'))


class RouteMixin(UnicodeMixin):
    '''Class for routing trees. This class is the base class for all
routing and handler classes in djpcms including, but not only, :class:`Site`,
:class:`djpcms.views.Application` and :class:`ViewHandler`.

.. attribute:: parent

    The :class:`RouteMixin` immediately before this route. This attribute
    is set by djpcms when building a new :class:`Site`.

.. attribute:: permissions

    The :class:`djpcms.cms.permissions.PermissionHandler`
    for this :class:`RouteMixin`.

.. attribute:: rel_route

    The relative :class:`Route` with respect :attr:`parent` for this instance.

.. attribute:: route

    The :class:`Route` for this instance. Calculated from :attr:`rel_route`
    and :attr:`parent`.

.. attribute:: path

    proxy to the :attr:`Route.path` attribute of :attr:`route`.
    It is the absolute path for this :class:`RouteMixin`.

.. attribute:: isbound

    ``True`` when the route is bound to a :class:`ResolverMixin` instance.

.. attribute:: root

    The root :class:`RouteMixin` instance for of this route. If this instance
    has :attr:`parent` set to ``None``, the :attr:`root` is equal to ``self``.

.. attribute:: is_root

    ``True`` if :attr:`root` is ``self``.

.. attribute:: tree

    The views non-recombining tree

.. attribute:: site

    The closes :class:`Site` instance for of this route.

.. attribute:: settings

    web site settings dictionary, available when :attr:`isbound` is ``True``.
'''
    PERM = VIEW

    def __init__(self, route):
        if not isinstance(route, Route):
            route = Route(route)
        self._rel_route = route
        self.local = {}
        self.internals = {}
        self.parent = None

    def __unicode__(self):
        return self.route.rule

    def __copy__(self):
        d = self.__dict__.copy()
        o = self.__class__.__new__(self.__class__)
        d['_rel_route'] = copy(self._rel_route)
        d['local'] = {}
        o.__dict__ = d
        o.parent = None
        return o

    def __deepcopy__(self, memo):
        return copy(self)

    @property
    def lock(self):
        if not 'lock' in self.local:
            self.local['lock'] = Lock()
        return self.local['lock']

    @property
    def route(self):
        return self.local['route']

    def _get_parent(self):
        return self.local['parent']
    def _set_parent(self, parent):
        self.local['parent'] = self._make_parent(parent)
    parent = property(_get_parent,_set_parent)

    def __get_rel_route(self):
        return self._rel_route
    def __set_rel_route(self, r):
        if self.route == self._rel_route:
            self._rel_route = r
            self.local['route'] = r
        else:
            br = self.route - self._rel_route
            self._rel_route = r
            self.local['route'] = br + r
    rel_route = property(__get_rel_route,__set_rel_route)

    @property
    def site(self):
        return self._site()

    @property
    def is_root(self):
        return self.parent is None

    @property
    def path(self):
        return self.route.path

    @property
    def root(self):
        if self.parent is not None:
            return self.parent.root
        else:
            return self

    @property
    def tree(self):
        if self.is_root:
            return self.local['tree']
        else:
            return self.root.tree

    @property
    def isbound(self):
        return self._isbound()

    def internal_data(self, name):
        v = self.internals.get(name)
        if v is None and self.parent:
            return self.parent.internal_data(name)
        else:
            return v

    @property
    def response(self):
        '''Access the site :ref:`response handler <response-handler>`.'''
        return self.internal_data('response_handler')

    @property
    def settings(self):
        return self.internal_data('settings')

    @property
    def search_engine(self):
        return self.internal_data('search_engine')

    @property
    def permissions(self):
        return self.internal_data('permissions')

    @property
    def meta_robots(self):
        return self.internal_data('meta_robots')

    @property
    def template(self):
        return self.internal_data('template')

    @property
    def User(self):
        return self.internal_data('User')

    @property
    def Page(self):
        return self.internal_data('Page')

    @property
    def BlockContent(self):
        return self.internal_data('BlockContent')

    @property
    def storage(self):
        return self.internal_data('storage')

    def encoding(self, request):
        '''Encoding for this route'''
        return self.settings.DEFAULT_CHARSET

    def content_type(self, request):
        '''Content type for this route'''
        return self.settings.DEFAULT_CONTENT_TYPE

    def cssgrid(self, request):
        settings = self.settings
        page = request.page
        layout = page.layout if page else None
        layout = layout or settings.LAYOUT_GRID_SYSTEM
        return get_cssgrid(layout)

    def instance_from_variables(self, environ, urlargs):
        '''Retrieve an instance form the variable part of the
 :attr:`route` attribute.

 :parameter urlargs: dictionary of url arguments.

 This function needs to be implemented by subclasses. By default it returns
 ``None``.
 '''
        pass

    def variables_from_instance(self, instance):
        '''Retrieve the url bits from an instance. It returns an iterator
 over key-value touples or a dictionary. This is the inverse of
 :meth:`instance_from_variables` function.'''
        raise StopIteration

    def get_url(self, urlargs, instance = None):
        '''Retrieve the :attr:`route` full *url* from a dictionary of
url attributes and, optionally, an instance of an element constructed
from the variable part of the url.'''
        if instance:
            urlargs.update(self.variables_from_instance(instance))
        try:
            return self.route.url(**urlargs)
        except:
            return None

    ############################################################################
    #    INTERNALS
    ############################################################################
    def _make_parent(self, parent):
        if parent is not None:
            if not isinstance(parent, RouteMixin):
                raise ValueError('parent must be an instance of RouteMixin.\
 Got "{0}"'.format(parent))
            self.local['route'] = parent.route + self._rel_route
        else:
            self.local['route'] = self._rel_route
        return parent

    def _site(self):
        raise NotImplementedError

    def _isbound(self):
        raise NotImplementedError


class ViewRenderer(Renderer):
    '''Base class:`Renderer` class for :class:`Site`, and
:class:`RendererMixin`.

.. attribute:: inherit_page

    If ``True`` and a page is not available for the view, the parent view
    page will be used (recursive).

    Default ``True``.
'''
    appmodel = None
    inherit_page = True

    def parent_instance(self, instance):
        '''Return the parent instance for *instance*. This is the instance
for the parent view. By default it returns *instance*. This function
is used by the :attr:`djpcms.Request.parent` attribute.'''
        return instance

    def add_media(self, request, media):
        request.media.add(media)

    def default_media(self, request):
        if not request.is_xhr:
            settings = self.settings
            m = media.Media(settings=settings)
            m.add_js(media.jquery_paths(settings))
            m.add_js(media.bootstrap(settings))
            m.add_js(settings.DEFAULT_JAVASCRIPT)
            if settings.DEFAULT_STYLE_SHEET:
                m.add_css(settings.DEFAULT_STYLE_SHEET)
            elif settings.STYLING:
                target = media.site_media_file(settings)
                if target:
                    m.add_css({'all': (target,)})
            m.add(self.media(request))
            return m

    def get_body_class(self, request):
        pass

    def underlying(self, request):
        return request


class RendererMixin(ViewRenderer):
    '''\
A :class:`djpcms.cms.ViewRenderer` used as mixin class for :class:`Application`
and :class:`ViewHandler`.

.. attribute:: appmodel

    An instance of :class:`Application` where this renderer belongs
    to or ``None``.

.. attribute:: name

    A name. Calculated from class name if not provided.

.. attribute:: description

    Useful description of the renderer in few words
    (no more than 20~30 characters). Used only when the
    :attr:`has_plugins` flag is set to ``True``.
    In this case its value is used when
    displaying menus of available plugins. If not defined it is
    calculated from the attribute name of the view
    in the :class:`Application` where it is declared.

    Default: ``None``.

.. attribute:: site

    instance of :class:`ApplicationSite` to which this renderer belongs to.

.. attribute:: pagination

    An instance of a :class:`djpcms.html.PaginationOptions` for specifying how
    several items will be paginated in the renderer. This atribute is used by
    :class:`Application` and :class:`View`.

    Default: ``None``.

.. attribute:: form

    The default :class:`djpcms.forms.Form` or :class:`djpcms.forms.HtmlForm`
    class used by the renderer.

    Default ``None``.

.. attribute:: in_nav

    Numeric value used to position elements in navigation. If equal to ``0``
    the element won't appear in any navigation.

    Default: ``0``

.. attribute:: has_plugins:

    If ``True`` the view can be placed in any page via the plugin API.
    (Check :class:`djpcms.plugins.ApplicationPlugin` for more info).

    Default: ``True``.

.. attribute:: ajax_enabled

    If this renderer has ajax enabled rendering views.

    Default: ``None``

.. attribute:: template_file

    Used to specify a template file or a tuple of template files.

    Default: ``None``.

.. attribute:: insitemap

    If ``True`` the view is included in site-map.

    Default: ``True``.

.. attribute:: settings

    proxy of the :attr:`ApplicationSite.settings` from :attr:`site` attribute
'''
    creation_counter = 0
    cache_control = None
    appmodel = None
    template_file = None
    name = None
    description = None
    form = None
    dialog_width = 'auto'
    dialog_height = 'auto'
    ajax_enabled = None
    pagination = None
    hidden = False
    in_nav = 0
    has_plugins = True
    insitemap = True
    parent_view = None
    body_class = None

    def __init__(self, name=None, parent_view=None, pagination=None,
                 ajax_enabled=None, form=None, template_file=None,
                 description=None, in_nav=None, has_plugins=None,
                 insitemap=None, body_class=None, view_ordering=None,
                 hidden=None, cache_control=None):
        self.creation_counter = RendererMixin.creation_counter
        self.view_ordering = view_ordering if view_ordering is not None else\
                                self.creation_counter
        RendererMixin.creation_counter += 1
        self.name = name if name is not None else self.name
        self.description = description if description is not None else\
                            self.description
        self.parent_view = parent_view if parent_view is not None\
                                 else self.parent_view
        self.pagination = pagination if pagination is not None\
                                     else self.pagination
        self.cache_control = cache_control or self.cache_control
        self.form = form if form is not None else self.form
        self.template_file = template_file or self.template_file
        if self.template_file:
            t = self.template_file
            if not (isinstance(t,list) or isinstance(t,tuple)):
                t = (t,)
            self.template_file = tuple(t)
        self.ajax_enabled = ajax_enabled if ajax_enabled is not None\
                                     else self.ajax_enabled
        self.hidden = hidden if hidden is not None else self.hidden
        if self.hidden:
            self.in_nav = 0
            self.insitemap = False
        else:
            self.in_nav = in_nav if in_nav is not None else self.in_nav
            self.insitemap = insitemap if insitemap is not None\
                                else self.insitemap
        self.has_plugins = has_plugins if has_plugins is not None else\
                             self.has_plugins
        if isinstance(form, forms.FormType):
            self.form = forms.HtmlForm(self.form)
        self.body_class = body_class if body_class is not None else\
                                self.body_class
        makename(self, self.name, self.description)

    # RESPONSES
    def get_response(self, request):
        '''Render a standard GET request (not an ajax request). By
default it returns the page layout. It invokes the :meth:`render`
method for this view.'''
        page = request.page
        layout = page.layout if page else 'default'
        try:
            layout = self.root.get_page_layout(layout)
        except:
            return request.render(request)
        else:
            return layout()

    def post_response(self, request):
        '''The post response handler. It invkoes the render method.'''
        return submit_form(request)

    def ajax_get_response(self, request):
        '''Default AJAX GET response. It renders and return a ajax dialog.'''
        text = request.render(block=True)
        content_type = request.REQUEST.get('content_type', 'json')
        media = request.media
        if content_type == 'json':
            js = ajax.dialog(request.environ,
                             hd=request.title,
                             bd=text,
                             width=self.dialog_width,
                             height=self.dialog_height,
                             modal=True)
        else:
            js = ajax.Text(request.environ, text)
        js.javascript(media.all_js)
        return js

    def ajax_post_response(self, request):
        '''Handle AJAX post requests. By default it invokes the
:meth:`post_response` method.'''
        return self.post_response(request)

    def render(self, request, **kwargs):
        '''Render the Current View. Must be implemented by sublasses'''
        return ''

    def query(self, request, **kwargs):
        '''This function implements a query on the :attr:`RedererMixin.model`
if available. By defaults it invoke the ``query`` method in the
:attr:`appmodel`.

:parameter kwargs: extra parameters for the query.
:rtype: an iterable instance over model instances.'''
        if self.appmodel:
            return self.appmodel.query(request, **kwargs)

    def model_fields(self, request, pagination=None):
        pagination = pagination or self.pagination
        if pagination:
            for head in pagination.list_display:
                yield head.code, head.name

    def success_message(self, request, response):
        return str(response)

    def for_user(self, request):
        '''Return an instance of a user model if the current renderer
belongs to a user, otherwise returns ``None``.'''
        return None

    def get_cache_control(self):
        cache_control = self.cache_control
        if not cache_control and self.appmodel:
            cache_control = self.appmodel.cache_control
        return cache_control


class ViewHandler(RouteMixin, RendererMixin):
    '''A virtual class inheriting from :class:`RouteMixin` and
:class:`RendererMixin` for handling http requests on a given
:class:`Route`. This class should not be used directly,
it is the base class of :class:`pageview` and :class:`djpcms.views.View`.

.. attribute:: _methods

    Tuple of request methods handled by ``self``.
    By default ``GET`` and ``POST`` only::

        _methods = ('get','post')

.. attribute:: object_view

    Flag indicating if the view is used to render or manipulate model instances.

    Default ``False``.

.. attribute:: ICON

    An icon for this view

    '''
    DEFAULT_METHOD = 'get'
    object_view = False
    ICON = None
    link_class = 'minibutton'
    default_title = None
    default_link = None
    link_text = True
    redirect_to_view = None
    logger = logging.getLogger('ViewHandler')

    _methods      = ('get',)

    def __init__(self, route='', parent=None, **kwargs):
        RouteMixin.__init__(self, route)
        RendererMixin.__init__(self, **kwargs)
        if parent is not None:
            self.parent = parent

    def __unicode__(self):
        return '%s: %s' % (self.name,self.path)

    @property
    def model(self):
        if self.appmodel:
            return self.appmodel.model

    @property
    def mapper(self):
        if self.appmodel:
            return self.appmodel.mapper

    def instance_from_variables(self, environ, urlargs):
        if self.appmodel:
            if self.object_view:
                return self.appmodel.instance_from_variables(environ, urlargs)

    def variables_from_instance(self, instance):
        if self.appmodel:
            if self.object_view:
                return self.appmodel.variables_from_instance(instance)
        return ()

    def model_fields(self, request, pagination=None):
        if self.appmodel:
            return self.appmodel.model_fields(request,
                                              pagination or self.pagination)
        return ()

    def __call__(self, request):
        method = request.method
        if not request.is_xhr:
            # not and AJAX REQUEST
            callable = getattr(self,'%s_response' % method)
        else:
            data = request.REQUEST
            ajax_action = forms.get_ajax_action(data)
            callable = getattr(self, 'ajax_%s_response' % method)
            if ajax_action:
                ajax_view = 'ajax__' + ajax_action
                if hasattr(self, ajax_view):
                    callable = getattr(self, ajax_view)
                else:
                    callable = getattr(self.appmodel, ajax_view, callable)
        return callable(request)

    def methods(self, request):
        '''Allowed request methods for this view.
        By default it returns :attr:`_methods`.
        '''
        return self._methods

    def title(self, request):
        '''View title'''
        page = request.page
        title = page.title if page else self.default_title
        link = self.linkname(request)
        if not title:
            return link
        elif link:
            link += ' '
        return escape(title.format(request.urlargs, request.instance, link))

    def linkname(self, request):
        '''Name to display in hyperlinks to this view.'''
        page = request.page
        link = page.link if page else self.default_link
        if not link:
            link = self.default_link or \
                    (self.appmodel.description if self.appmodel else '')
        return escape(link.format(request.urlargs,request.instance))

    def breadcrumb(self, request):
        return self.linkname(request)

    def is_soft(self, request):
        '''Check if this view is a root of a navigation.'''
        page = request.page
        return False if not page else page.soft_root

    def in_navigation(self, request):
        '''Hook for modifying the in_navigation property.
This default implementation should suffice'''
        page = request.page
        return page.in_navigation if page else 0

    def redirect_url(self, request, instance=None, name=None):
        '''Call the :meth:`Application.redirect_url` by default.'''
        if self.appmodel:
            return self.appmodel.redirect_url(request, instance, name)

    def warning_message(self, request):
        return None

    def meta_charset(self, request):
        return self.settings.DEFAULT_CHARSET

    def meta_description(self, request):
        return self.settings.META_DESCRIPTION

    def meta_keywords(self, request):
        return self.settings.META_KEYWORDS

    def meta_author(self, request):
        return self.settings.META_AUTHOR

    def meta_viewport(self, request):
        return self.settings.META_VIEWPORT

    def get_body_class(self, request):
        page = request.page
        if page and page.body_class:
            return page.body_class
        elif self.body_class:
            return self.body_class
        elif self.appmodel:
            return self.appmodel.body_class

    def _site(self):
        if self.appmodel:
            return self.appmodel.site
        else:
            return self.parent


class pageview(ViewHandler):
    '''A :class:`ViewHandler` for flat pages. A flat page does not mean
static data, it means it is view not available in any :class;`Application`.
In this case the view will display plugins which are of course dynamic.
This view is only available when a :class:`djpcms.Page` implementation
is installed.

:parameter page: Instance of a :class:`djpcms.Page`.
:parameter parent: the :class:`djpcms.ResolverMixin` which is the parent of
    this view. If it is an instance of a class:`Application`, it will also be
    the :attr:`RendererMixin.appmodel` attribute for the view.'''
    name = 'flat'
    def __init__(self, page, parent):
        if isinstance(parent, RendererMixin):
            self.appmodel = parent
        self.page = page
        super(pageview, self).__init__(self.page.route, parent)


class url_match(object):
    __slots__ = ('_handler', 'args', 'remaining')
    def __init__(self, handler, args, remaining):
        self._handler = handler
        self.args = args
        self.remaining = remaining

    def handler(self):
        if not isinstance(self._handler, ViewHandler):
            return ViewHandler(self.remaining, self._handler)
        else:
            return self._handler