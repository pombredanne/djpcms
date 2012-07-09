import logging

import djpcms
from djpcms.utils.httpurl import range
from djpcms import forms, html, ajax
from djpcms.utils.text import nicename, UnicodeMixin, slugify, escape
from djpcms.cms import RouteMixin, ViewRenderer

    
__all__ = ['RendererMixin',
           'djpcmsview',
           'pageview']
    
    
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
    
    
class RendererMixin(ViewRenderer):
    '''\
A :class:`djpcms.cms.ViewRenderer` used as mixin class for :class:`Application`
and :class:`djpcmsview`.

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
    in_nav = 0
    has_plugins = True
    insitemap = True
    parent_view = None
    body_class = None
    
    def __init__(self, name=None, parent_view=None, pagination=None,
                 ajax_enabled=None, form=None, template_file=None,
                 description=None, in_nav=None, has_plugins=None,
                 insitemap=None, body_class=None, view_ordering=None,
                 cache_control=None):
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
        self.in_nav = in_nav if in_nav is not None else self.in_nav
        self.has_plugins = has_plugins if has_plugins is not None else\
                             self.has_plugins
        self.insitemap = insitemap if insitemap is not None else self.insitemap
        if isinstance(form, forms.FormType):
            self.form = forms.HtmlForm(self.form)
        self.body_class = body_class if body_class is not None else\
                                self.body_class
        makename(self, self.name, self.description)
            
    def render(self, request, **kwargs):
        '''Render the Current View and return a safe string.
This function is implemented by subclasses of :class:`View`.
By default it returns an empty string if the view is a :class:`pageview`
other wise the ``render`` method of the :attr:`appmodel`.'''
        if self.appmodel:
            return self.appmodel.render(request, **kwargs)
        else:
            return ''
        
    def query(self, request, **kwargs):
        '''This function implements a query on the :attr:`RedererMixin.model`
if available. By defaults it invoke the ``query`` method in the
:attr:`appmodel`.

:parameter kwargs: extra parameters for the query.
:rtype: an iterable instance over model instances.'''
        if self.appmodel:
            return self.appmodel.query(request, **kwargs)
    
    def for_user(self, request):
        '''Return an instance of a user model if the current renderer
belongs to a user, otherwise returns ``None``.'''
        return None
    
    def get_cache_control(self):
        cache_control = self.cache_control
        if not cache_control and self.appmodel:
            cache_control = self.appmodel.cache_control
        return cache_control


class djpcmsview(RouteMixin, RendererMixin):
    '''A virtual class inheriting from :class:`RendererMixin`
and :class:`djpcms.core.RouteMixin` for handling http requests on a given
:class:`djpcms.Route`. This class should not be used directly,
it is the base class of :class:`pageview` and :class:`View`.
    
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
    logger = logging.getLogger('djpcmsview')
    
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
    
    def __call__(self, request):
        method = request.method
        if not request.is_xhr:
            callable = getattr(self,'%s_response' % method)
        else:
            data = request.REQUEST
            ajax_action = forms.get_ajax_action(data)
            callable = getattr(self,'ajax_%s_response' % method)
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
    
    def underlying(self, request):
        return request
    
    def is_soft(self, request):
        page = request.page
        return False if not page else page.soft_root
    
    def inner_contents(self, request, inner_template):
        site = self.site
        InnerContent(request, editing)
        for b in range(inner_template.numblocks()):
                cb['content%s' % b] = BlockContentGen(request, b, editing)
        
    def get_response(self, request, editing=False):
        '''Render a standard GET request (not an ajax request). By
default it returns the page layout.'''
        page = request.page
        layout = page.layout if page else 'default'
        try:
            layout = self.root.get_page_layout(layout)
        except:
            return self.render(request)
        else:
            return layout()
    
    def post_response(self, request):
        '''The post response handler.'''
        return self.get_response(request)
    
    def ajax_get_response(self, request):
        text = self.render(request)
        content_type = request.REQUEST.get('content_type', 'json')
        if content_type == 'json':
            return ajax.dialog(request.environ,
                               hd=request.title,
                               bd=text,
                               width=self.dialog_width,
                               height=self.dialog_height,
                               modal=True)
        else:
            return ajax.Text(request.environ, text)
    
    def ajax_post_response(self, request):
        '''Handle AJAX post requests'''
        return self.post_response(request)
    
    def in_navigation(self, request):
        '''
        Hook for modifying the in_navigation property.
        This default implementation should suffice
        '''
        page = request.page
        if page:
            return page.in_navigation
        else:
            return 0
    
    def redirect_url(self, request, instance = None, name = None):
        '''Call the :meth:`Application.redirect_url` by default.'''
        appmodel = self.appmodel
        if appmodel:
            return appmodel.redirect_url(request, instance, name)
        return '/'
    
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
        
        
class pageview(djpcmsview):
    '''A :class:`djpcmsview` for flat pages. A flat page does not mean
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
    