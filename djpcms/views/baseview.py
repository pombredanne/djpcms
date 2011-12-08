import logging

from py2py3 import range

import djpcms
from djpcms import UnicodeMixin, forms, http, html, ajax, Route, RouteMixin,\
                        Http404
from djpcms.utils import parentpath, slugify
from djpcms.utils.urls import openedurl
from djpcms.utils.text import nicename

from .contentgenerator import InnerContent

    
__all__ = ['RendererMixin',
           'djpcmsview',
           'pageview']
    
    
SPLITTER = '-'

def makename(self, name, description):
    name = name or self.name
    if not name:
        name = openedurl(self.path).replace('/','_')\
                                   .replace('<','')\
                                   .replace('>','')
        if not name:
            name = self.__class__.__name__.lower()
    name = name.replace(SPLITTER,'_')
    self.description = description or self.description or nicename(name)
    self.name = str(slugify(name.lower(),rtx='_'))
    
    
class RendererMixin(html.Renderer):
    '''\
A :class:`djpcms.html.Renderer` used as mixin class for :class:`Application`
and :class:`djpcmsview`.

.. attribute:: appmodel

    An instance of :class:`Application` where this renderer belongs
    to or ``None``.
    
.. attribute:: name

    A name. Calculated from class name if not provided.
    
.. attribute:: description

    Useful description of the renderer in few words
    (no more than 20~30 characters). Used only when the
    :attr:`has_plugin` flag is set to ``True``.
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
    
.. attribute:: has_plugin:

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
    
    def __init__(self, name = None, parent_view = None, pagination = None,
                 ajax_enabled = None, form = None, template_file = None,
                 description = None, in_nav = None, has_plugins = None,
                 insitemap = None, body_class = None):
        self.creation_counter = RendererMixin.creation_counter
        RendererMixin.creation_counter += 1
        self.name = name if name is not None else self.name
        self.description = description if description is not None else\
                            self.description
        self.parent_view = parent_view if parent_view is not None\
                                 else self.parent_view
        self.pagination = pagination if pagination is not None\
                                     else self.pagination
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
        if isinstance(form,forms.FormType):
            self.form = forms.HtmlForm(self.form)
        self.body_class = body_class if body_class is not None else\
                                self.body_class
        makename(self, self.name, self.description)
            
    def render(self, request):
        '''\
Render the Current View and return a safe string.
This function is implemented by subclasses of :class:`View`.
By default it returns an empty string if the view is a :class:`pageview`
other wise the ``render`` method of the :attr:`appmodel`.'''
        if self.appmodel:
            return self.appmodel.render(request)
        else:
            return ''
        
    def query(self, request, **kwargs):
        '''This function implements a query.'''
        if self.appmodel:
            return self.appmodel.query(request, **kwargs)
    
    def for_user(self, request):
        '''Return an instance of a user model if the current renderer
belongs to a user, otherwise returns ``None``.'''
        return None
    
    def redirect(self, request, url):
        '''An utility which return a redirect response'''
        if request.is_xhr:
            return ajax.jredirect(url)
        else:
            return http.ResponseRedirect(url)            


class djpcmsview(RouteMixin,RendererMixin):
    '''A virtual class inheriting from :class:`RendererMixin`
and :class:`djpcms.RouteMixin` for handling http requests on a given
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
    PERM = djpcms.VIEW
    DEFAULT_METHOD = 'get'
    object_view = False
    ICON = None
    link_class = 'minibutton'
    default_title = None
    default_link = None
    link_text = True
    logger = logging.getLogger('djpcmsview')
    
    _methods      = ('get','post')
    
    def __init__(self, route = '', parent = None, **kwargs):
        RouteMixin.__init__(self, route, parent)
        RendererMixin.__init__(self, **kwargs)
        
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
        
    def instance_from_variables(self, urlargs):
        if self.appmodel:
            if self.object_view:
                return self.appmodel.instance_from_variables(urlargs)
        
    def variables_from_instance(self, instance):
        if self.appmodel:
            if self.object_view:
                return self.appmodel.variables_from_instance(instance)
        return ()
    
    def __call__(self, request):
        is_xhr = request.is_xhr
        method = request.method
        if not request.is_xhr:
            return getattr(self,'%s_response' % method)(request)
        
        data = request.REQUEST
        ajax_action = forms.get_ajax_action(data)
        callable = getattr(self,'ajax_%s_response' % method)
        if ajax_action:
            ajax_view = 'ajax__' + ajax_action
            if hasattr(self,ajax_view):
                callable = getattr(self, ajax_view)
            else:
                callable = getattr(self.appmodel, ajax_view, callable)
        #TODO
        #make this asynchronous
        res = callable(request)
        content = res.dumps().encode('latin-1','replace')
        return http.Response(content = content,
                             content_type = res.mimetype())
        #else:
        #    return res
        #except Exception as e:
        #    if is_ajax:
        #        res = handle_ajax_error(self,e)
        #        content = res.dumps().encode('latin-1','replace')
        #        return http.Response(content = content,
        #                             content_type = res.mimetype())
         #   else:
         #       raise
    
    
    def methods(self, request):
        '''Allowed request methods for this view.
        By default it returns :attr:`_methods`.
        '''
        return self._methods
        
    def title(self, request):
        '''View title'''
        page = request.page
        title = page.title if page else None
        if not title:
            title = self.default_title or \
                    (self.appmodel.description if self.appmodel else 'view')
        return title.format(request.urlargs,request.instance)
    
    def linkname(self, request):
        '''Name to display in hyperlinks to this view.'''
        page = request.page
        link = page.link if page else None
        if not link:
            link = self.default_link or \
                    (self.appmodel.description if self.appmodel else 'view')
        return link.format(request.urlargs,request.instance)
    
    def breadcrumb(self, request):
        return self.linkname(request)
    
    def is_soft(self, request):
        page = request.page
        return False if not page else page.soft_root
    
    def inner_contents(self, request, inner_template):
        site = self.site
        InnerContent(request, editing)
        for b in range(inner_template.numblocks()):
                cb['content%s' % b] = BlockContentGen(request, b, editing)
        
    def get_context(self, request, editing = False):
        '''View context as a dictionary.'''
        page = request.page
        inner_template = page.inner_template if page else None

        if inner_template:
            inner = InnerContent(request, inner_template, editing)
        else:
            # No page or no inner_template. Get the inner content directly
            inner = self.render(request)

        # if status_code is an attribute we consider this as the response
        # object and we return it.
        if hasattr(inner,'status_code'):
            return inner
        
        return {'title': request.title,
                'body_class': self.get_body_class(request),
                'inner': inner}

    def get_response(self, request):
        '''Get response handler.'''
        context = self.get_context(request)
        if hasattr(context,'status_code'):
            return context
        return self.render_page(request, context)
    
    def post_response(self, request):
        '''Get response handler.'''
        return self.get_response(request)
    
    def ajax_get_response(self, request):
        html = self.render(request)
        return ajax.dialog(hd = request.title,
                           bd = html,
                           width = self.dialog_width,
                           height = self.dialog_height,
                           modal = True)
    
    def ajax_post_response(self, request):
        '''Handle AJAX post requests'''
        data = request.REQUEST
        action = forms.get_ajax_action(data)
        if action == forms.CANCEL_KEY:
            next = data.get(forms.REFERER_KEY,None)
            next = self.defaultredirect(request, next = next)
            return ajax.jredirect(next)
        return self.post_response(request)
    
    def has_permission(self, request, page = None, obj = None, user = None):
        '''Check for page view permissions.'''
        if page:
            return self.permissions.has(request,djpcms.VIEW,page,user=user)
        else:
            return True
    
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
    
    def defaultredirect(self, request, next = None,
                        instance = None, **kwargs):
        '''This function is used to build a redirect ``url`` for ``self``.
It is called by ``djpcms`` only when a redirect is needed.

:parameter request: HttpRequest object.
:parameter url: optional ``url`` provided.
:parameter instance: optional instance of a model.
:parameter kwargs: additional url bits.

By default it returns ``next`` if available, otherwise ``request.path``.
'''
        if next:
            return request.build_absolute_uri(next)
        else:
            return request.environ.get('HTTP_REFERER')
    
    def nextviewurl(self, request):
        '''Calculate the best possible url for a possible next view.
By default it is ``djp.url``'''
        return request.path
    
    def warning_message(self, request):
        return None
        
    def meta_description(self, request):
        return self.settings.META_DESCRIPTION
    
    def meta_keywords(self, request):
        return self.settings.META_KEYWORDS
    
    def meta_author(self, request):
        return self.settings.META_AUTHOR
      
    def get_body_class(self, request):
        page = request.page
        if page and page.body_class:
            return page.body_class
        elif self.body_class:
            return self.body_class
        elif self.appmodel:
            return self.appmodel.body_class
        
        
class pageview(djpcmsview):
    '''A :class:`djpcmsview` for flat pages. A flat page does not mean
 static data, it means there is not a specific application associate with it.'''
    name = 'flat'
    def __init__(self, page, handler):
        if isinstance(handler,RendererMixin):
            self.appmodel = handler
        self.page = page
        super(pageview,self).__init__(self.page.route, handler)
    