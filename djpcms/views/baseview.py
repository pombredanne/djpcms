import logging

from py2py3 import range

import djpcms
from djpcms import UnicodeMixin, forms
from djpcms.utils.ajax import jredirect, dialog
from djpcms.html import Media
from djpcms.template import loader
from djpcms.utils import parentpath

from .response import DjpResponse
from .contentgenerator import BlockContentGen
from .regex import RegExUrl, RouteMixin

    
__all__ = ['RendererMixin',
           'djpcmsview',
           'pageview']
    
    
class RendererMixin(UnicodeMixin,RouteMixin):
    '''\
A mixin class for rendering objects

    .. attribute:: appmodel
    
        The application model wher the renedrer is defined.
        
    .. attribute:: template_name
     
        Used to specify a template file or a tuple of template files.
'''
    parent = None
    appmodel = None
    template_name = None
    name = None
    description = None
    dialog_width = 400
    
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
    object_view = False
    logger = logging.getLogger('djpcmsview')
    
    _methods      = ('get','post')

    def get_media(self):
        return Media()
    
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
        '''View title.'''
        page = djp.page
        if page:
            return page.title
        else:
            return None
    
    def linkname(self, djp):
        page = djp.page
        if page:
            return page.link
        else:
            return 'link'
    
    def specialkwargs(self, page, kwargs):
        return kwargs
    
    def preprocess(self, djp):
        pass
    
    def extra_content(self, djp, c):
        pass
    
    def get_context(self, djp, editing = False):
        request = djp.request
        site    = self.site
        http    = site.http
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
            inner = page.inner_template.render(loader.context(cb, request=request))
        else:
            # No page or no inner_template. Get the inner content directly
            inner = self.render(djp)
            if isinstance(inner,http.HttpResponse):
                return inner
        
        context['inner'] = inner
        return context

    def get_response(self, djp):
        '''Get response handler.'''
        context = self.get_context(djp)
        return djp.render_to_response(context)
    
    def post_response(self, djp):
        '''Get response handler.'''
        raise NotImplementedError('Post response not implemented')
    
    def ajax_get_response(self, djp):
        html = self.render(djp)
        return dialog(hd = djp.title,
                      bd = html,
                      width = self.dialog_width,
                      modal = True)
    
    def ajax_post_response(self, djp):
        '''Handle AJAX post requests'''
        request = djp.request
        data = request.data_dict
        action = forms.get_ajax_action(data)
        if action == forms.CANCEL_KEY:
            next = data.get(forms.REFERER_KEY,None)
            next = self.defaultredirect(djp.request, next = next, **djp.kwargs)
            return jredirect(next)
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
