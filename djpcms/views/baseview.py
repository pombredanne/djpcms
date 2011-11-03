import logging

from py2py3 import range

import djpcms
from djpcms import UnicodeMixin, forms, http, html, ajax, RegExUrl, RouteMixin
from djpcms.utils import parentpath

from .response import DjpResponse
from .contentgenerator import BlockContentGen

    
__all__ = ['RendererMixin',
           'djpcmsview',
           'pageview']
    
    
class RendererMixin(UnicodeMixin,RouteMixin,html.Renderer):
    '''\
A mixin class for rendering objects as HTML

    .. attribute:: appmodel
    
        The application model wher the renedrer is defined.
        
    .. attribute:: template_name
     
        Used to specify a template file or a tuple of template files.
'''
    parent = None
    appmodel = None
    template_name = None
    name = None
    dialog_width = 'auto'
    dialog_height = 'auto'
    ajax_enabled = None
    list_display = ()
    
    def render(self, djp):
        '''\
Render the Current View and return a safe string.
This function is implemented by subclasses of :class:`djpcms.views.View`.
By default it returns an empty string if the view is a :class:`djpcms.views.pageview`
other wise the ``render`` method of the :attr:`appmodel`.

:parameter djp: instance of :class:`djpcms.views.DjpResponse`.'''
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
    '''A :class:`djpcms.views.RendererMixin` class for handling
http requests.
    
    .. attribute:: _methods

        Tuple of request methods handled by ``self``. By default ``GET`` and ``POST`` only::
        
            _methods = ('get','post')
    
    .. attribute:: object_view
    
        Flag indicating if the view is used to render or manipulate model instances.
        
        Default ``False``.
             
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
    
    def names(self):
        return None
    
    def get_url(self, djp, **urlargs):
        return djp.request.path
    
    def __call__(self, request, **kwargs):
        return DjpResponse(request, self, **kwargs)
    
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
    
    def get_context(self, djp, editing = False):
        '''View context as a dictionary.'''
        request = djp.request
        site    = self.site
        page    = djp.page
        inner_template  = None
        context = {'title':djp.title}
                    
        if page:
            inner_template = page.inner_template
            if not inner_template:
                inner_template = site.add_default_inner_template(page)
            
        if inner_template:
            cb = {'djp':  djp}
            for b in range(inner_template.numblocks()):
                cb['content%s' % b] = BlockContentGen(djp, b, editing)
            loader = site.template
            inner = page.inner_template.render(
                                    loader,
                                    loader.context(cb, request=request))
        else:
            # No page or no inner_template. Get the inner content directly
            inner = self.render(djp)
            if isinstance(inner,http.Response):
                return inner
        
        context['inner'] = inner
        return context

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
        self.site = site
        self.page = page  
        
    def route(self):
        return RegExUrl(self.page.url)
    
    def get_url(self, djp, **urlargs):
        return self.page.url
    
    def is_soft(self, djp):
        return self.page.soft_root
