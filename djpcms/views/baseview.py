import logging

from py2py3 import range

import djpcms
from djpcms import UnicodeMixin, forms, http, html, ajax, Route, RouteMixin
from djpcms.utils import parentpath

from .response import DjpResponse
from .contentgenerator import InnerContent

    
__all__ = ['RendererMixin',
           'djpcmsview',
           'pageview']
    
    
class RendererMixin(UnicodeMixin,RouteMixin,html.Renderer):
    '''\
A :class:`djpcms.html.Renderer` used as mixin class for :class:`Application`
and :class:`djpcmsview`.

.. attribute:: appmodel

    An instance of :class:`Application` where this renderer belongs
    to or ``None``.
    
.. attribute:: parent

    An instance of a :class:`RendererMixin` which holds this renderer
    or ``None``.
    
.. attribute:: name

    A name. Calculated from class name if not provided.
    
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
    
.. attribute:: has_plugin:

    If ``True`` the view can be placed in any page via the plugin API.
    (Check :class:`djpcms.plugins.ApplicationPlugin` for more info).
    
    Default: ``True``.
    
.. attribute:: ajax_enabled

    If this renderer has ajax enabled rendering views.
    
    Default: ``None``
    
.. attribute:: template_name
 
    Used to specify a template file or a tuple of template files.
    
    Default: ``None``.
    
.. attribute:: settings

    proxy of the :attr:`ApplicationSite.settings` from :attr:`site` attribute
'''
    parent = None
    appmodel = None
    template_name = None
    name = None
    description = None
    form = None
    dialog_width = 'auto'
    dialog_height = 'auto'
    ajax_enabled = None
    pagination = None
    in_nav = None
    has_plugins = True
    insitemap = True
    
    def __init__(self, parent = None, name = None, pagination = None,
                 ajax_enabled = None, form = None, template_name = None,
                 description = None, in_nav = None, has_plugins = None,
                 insitemap = None):
        self.parent = parent if parent is not None else self.parent
        self.name = name if name is not None else self.name
        self.description = description if description is not None else\
                            self.description
        self.pagination = pagination if pagination is not None\
                                     else self.pagination
        self.form = form if form is not None else self.form
        self.template_name = template_name or self.template_name
        if self.template_name:
            t = self.template_name
            if not (isinstance(t,list) or isinstance(t,tuple)):
                t = (t,)
            self.template_name = tuple(t)
        self.ajax_enabled = ajax_enabled if ajax_enabled is not None\
                                     else self.ajax_enabled
        self.in_nav = in_nav if in_nav is not None else self.in_nav
        self.has_plugins = has_plugins if has_plugins is not None else\
                             self.has_plugins
        self.insitemap = insitemap if insitemap is not None else self.insitemap
        if isinstance(form,forms.FormType):
            self.form = forms.HtmlForm(self.form)
    
    @property
    def site(self):
        if self.appmodel:
            return self.appmodel.site
        else:
            return getattr(self,'_site',None)
        
    @property
    def settings(self):
        if self.site:
            return self.site.settings
            
    def render(self, djp):
        '''\
Render the Current View and return a safe string.
This function is implemented by subclasses of :class:`View`.
By default it returns an empty string if the view is a :class:`pageview`
other wise the ``render`` method of the :attr:`appmodel`.

:parameter djp: instance of :class:`DjpResponse`.'''
        if self.appmodel:
            return self.appmodel.render(djp)
        else:
            return ''
    
    def for_user(self, djp):
        '''Return an instance of a user model if the current renderer
belongs to a user, otherwise returns ``None``.'''
        return None
    
    def redirect(self, request, url):
        '''An utility which return a redirect response'''
        if request.is_xhr:
            return ajax.jredirect(url)
        else:
            return http.ResponseRedirect(url)


class djpcmsview(RendererMixin):
    '''A virtual :class:`RendererMixin` class for handling http requests
on a given url. This class should not be used directly, it is the base class
of :class:`pageview` and :class:`View`.
    
.. attribute:: _methods

    Tuple of request methods handled by ``self``. By default ``GET`` and ``POST`` only::
    
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
    
    def __unicode__(self):
        try:
            return '%s: %s' % (self.name,self.path())
        except:
            return self.name
        
    @property
    def model(self):
        if self.appmodel:
            return self.appmodel.model
    
    def names(self):
        return None
    
    def get_url(self, djp, **urlargs):
        return djp.request.path
    
    def __call__(self, request, instance = None, **kwargs):
        djp = None
        if instance:
            djp = request.DJPCMS.djp_from_instance(self, instance)
            if not djp:
                kwargs['instance'] = instance
        if not djp:
            djp = DjpResponse(request, self, kwargs)
        return djp
    
    def methods(self, request):
        '''Allowed request methods for this view.
        By default it returns :attr:`_methods`.
        '''
        return self._methods
        
    def title(self, djp):
        '''View title'''
        page = djp.page
        title = page.title if page else None
        if not title:
            title = self.default_title or \
                    (self.appmodel.description if self.appmodel else 'view')
        return title.format(djp.kwargs)
    
    def linkname(self, djp):
        '''Name to display in hyperlinks to this view.'''
        page = djp.page
        link = page.link if page else None
        if not link:
            link = self.default_link or \
                    (self.appmodel.description if self.appmodel else 'view')
        return link.format(djp.kwargs)
    
    def breadcrumb(self, djp):
        return self.linkname(djp)
    
    def specialkwargs(self, page, kwargs):
        return kwargs
    
    def preprocess(self, djp):
        pass
    
    def extra_content(self, djp, c):
        pass
    
    def inner_contents(self, inner_template):
        site = self.site
        InnerContent(djp, editing)
        for b in range(inner_template.numblocks()):
                cb['content%s' % b] = BlockContentGen(djp, b, editing)
        
    def get_context(self, djp, editing = False):
        '''View context as a dictionary.'''
        request = djp.request
        page    = djp.page
        inner_template = page.inner_template if page else None

        if inner_template:
            inner = InnerContent(djp, inner_template, editing)
        else:
            # No page or no inner_template. Get the inner content directly
            inner = self.render(djp)

        # if status_code is an attribute we consider this as the response
        # object and we return it.
        if hasattr(inner,'status_code'):
            return inner
        
        return {'title': djp.title,
                'inner': inner}

    def get_response(self, djp):
        '''Get response handler.'''
        context = self.get_context(djp)
        return djp.render_to_response(context)
    
    def default_post(self, djp):
        '''Get response handler.'''
        raise NotImplementedError('Post response not implemented')
    
    def post_response(self, djp):
        '''Get response handler.'''
        return self.default_post(djp)
    
    def ajax_get_response(self, djp):
        html = self.render(djp)
        return ajax.dialog(hd = djp.title,
                           bd = html,
                           width = self.dialog_width,
                           height = self.dialog_height,
                           modal = True)
    
    def ajax_post_response(self, djp):
        '''Handle AJAX post requests'''
        request = djp.request
        data = request.REQUEST
        action = forms.get_ajax_action(data)
        if action == forms.CANCEL_KEY:
            next = data.get(forms.REFERER_KEY,None)
            next = self.defaultredirect(djp.request, next = next,
                                        **djp.kwargs)
            return ajax.jredirect(next)
        return self.default_post(djp)
    
    def has_permission(self, request, page = None, obj = None, user = None):
        '''Check for page view permissions.'''
        if page:
            return self.site.permissions.has(request,djpcms.VIEW,page,user=user)
        else:
            return True
    
    def in_navigation(self, request, page):
        '''
        Hook for modifying the in_navigation property.
        This default implementation should suffice
        '''
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
    
    def nextviewurl(self, djp):
        '''Calculate the best possible url for a possible next view.
By default it is ``djp.url``'''
        return djp.request.path
    
    def warning_message(self, djp):
        return None


class pageview(djpcmsview):
    '''A :class:`djpcmsview` for flat pages. A flat page does not mean
 static data, it means there is not a specific application associate with it.'''
    name = 'flat'
    def __init__(self, page, site):
        self._site = site
        self.page = page
        super(pageview,self).__init__()  
        
    def route(self):
        return Route(self.page.url)
    
    def get_url(self, djp, **urlargs):
        return self.page.url
    
    def is_soft(self, djp):
        return self.page.soft_root
