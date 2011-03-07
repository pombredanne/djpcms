import sys
import traceback
from copy import copy

from djpcms.utils.ajax import jredirect, jservererror
from djpcms.template import loader
from djpcms.utils import lazyattr, logtrace
from djpcms.utils.navigation import Navigator, Breadcrumbs
from djpcms.core.exceptions import ViewDoesNotExist

__all__ = ['DjpResponse']


class DjpResponse(object):
    '''Djpcms Http Response class. It contains information associated with a given url.
        
        .. attribute: request
        
            a HttpRequest instance
            
        .. attribute: view
        
            instance of :class:`djpcms.views.baseview.djpcmsview`
            
        .. attribute: url
        
            url associated with response. Note this url is not always the same as request.path.
        
        .. attribute: media
        
            Object carrying information about the media to be added to the HTML page.
            It is filled during rendering of all plugins and views.
    '''
    def __init__(self, request, view, wrapper = None, prefix = None, **kwargs):
        self.request    = request
        self.view       = view
        self.kwargs     = kwargs
        site            = request.site
        self.is_xhr     = request.is_xhr
        self.site       = site
        self.settings   = site.settings
        self.http       = site.http
        self.css        = self.settings.HTML_CLASSES
        self.wrapper    = wrapper
        self.prefix     = prefix
    
    def __repr__(self):
        return self.url
    
    def __str__(self):
        return self.__repr__()
    
    def __call__(self, prefix = None, wrapper = None):
        djp = copy.copy(self)
        djp.prefix  = prefix
        djp.wrapper = wrapper
        return djp
    
    def is_ajax(self):
        return self.request.is_ajax()
    
    def is_soft(self):
        return self.view.is_soft(self)
    
    def own_view(self):
        return self.url == self.request.path
    
    def underlying(self):
        '''If the current wrapper is for an editing view,
return the wrapper with the underlying view.'''
        if self.view.editurl:
            return self.view._view(self.request, **self.kwargs)
        else:
            return self
    
    def get_linkname(self):
        return self.view.linkname(self) or self.url
    linkname = property(get_linkname)
        
    def get_title(self):
        return self.view.title(self)
    title = property(get_title)
    
    def bodybits(self):
        return self.view.bodybits(self.page)
    
    def contentbits(self):
        return self.view.contentbits(self.page)
    
    def set_content_type(self, ct):
        h = self._headers['content-type']
        h[1] = ct
        
    def __get_media(self):
        media = getattr(self,'_media',None)
        if not media:
            media = self.view.get_media()
            setattr(self,'_media',media)
        return media
    def __set_media(self, other):
        setattr(self,'_media',other)
    media = property(__get_media,__set_media)
    
    def getdata(self, name):
        '''Extract data out of url dictionary. Return ``None`` if ``name`` is not in the dictionary.'''
        self.url
        return self.kwargs.get(name,None)
    
    @lazyattr
    def in_navigation(self):
        return self.view.in_navigation(self.request, self.page)
    
    @lazyattr
    def _get_page(self):
        '''Get the page object
        '''
        return self.view.get_page(self)
    page = property(_get_page)
    
    @lazyattr
    def get_url(self):
        '''Build the url for this application view.'''
        return self.view.get_url(self)
    url = property(get_url)
    
    @lazyattr
    def _get_template(self):
        return self.view.get_template(self.request, self.page)
    template_file = property(_get_template)
    
    @lazyattr
    def _get_parent(self):
        '''Parent Response object, that is a response object associated with
the parent of the embedded view.'''
        return self.view.parentresponse(self)
    parent = property(_get_parent)
    
    @lazyattr
    def get_children(self):
        self.instance
        return self.view.children(self, **self.kwargs) or []
    children = property(get_children)
    
    @property
    def instance(self):
        if self.view.object_view:
            kwargs = self.kwargs
            if 'instance' not in kwargs:
                self.url
            return kwargs['instance']
        
    def has_own_page(self):
        '''Return ``True`` if the response has its own :class:djpcms.models.Page` object.
        '''
        page = self.page
        if page:
            appv = getattr(self.view,'code',None)
            if appv:
                return page.application_view == appv
            else:
                return page.url == self.url
        return False
            
    def robots(self):
        '''Robots
        '''
        if self.view.has_permission(self.request, self.page, user = None):
            if not self.page or self.page.insitemap:
                return 'ALL'
        return 'NONE,NOARCHIVE'
        
    def response(self):
        '''return the type of response or an instance of HttpResponse
        '''
        view    = self.view
        request = self.request
        is_ajax = request.is_xhr
        page    = self.page
        site    = request.site
        http    = site.http
        method  = request.method.lower()
        
        # Check for page view permissions
        if not view.has_permission(request, page, self.instance):
            return view.permissionDenied(self)
        
        # chanse to bail out early
        re = view.preprocess(self)
        if isinstance(re,http.HttpResponse):
            return re
            
        if not is_ajax:
            # If user not authenticated set a test cookie  
            if not request.user.is_authenticated() and method == 'get':
                request.session.set_test_cookie()

            if method not in (m.lower() for m in view.methods(request)):
                raise http.HttpException(405,
                                         msg='method {0} is not allowed'.format(method))
        
            return getattr(view,'%s_response' % method)(self)
        else:
            # AJAX RESPONSE
            try:
                if method not in (m.lower() for m in view.methods(request)):
                    raise ViewDoesNotExist('{0} method not available'.format(method))
                res = getattr(view,'ajax_%s_response' % method)(self)
            except ViewDoesNotExist as e:
                res = jservererror(str(e), url = request.path)
            except Exception as e:
                if site.settings.DEBUG:
                    exc_info = sys.exc_info()
                    stack_trace = '\n'.join(traceback.format_exception(*exc_info))
                    logtrace(self.view.logger, request, exc_info)
                    res = jservererror(stack_trace, url = self.url)
                else:
                    raise e
            return self.http.HttpResponse(res.dumps(),
                                          mimetype = res.mimetype())
    
    def render_to_response(self, context):
        css = self.css
        media = self.media
        sitenav = Navigator(self,
                            classes = css.main_nav,
                            levels = self.settings.SITE_NAVIGATION_LEVELS)
        
        context.update({'robots':     self.robots(),
                        'media':      media,
                        'sitenav':    sitenav})
        if self.settings.ENABLE_BREADCRUMBS:
            b = getattr(self,'breadcrumbs',None)
            if b is None:
                b = Breadcrumbs(self,min_length = self.settings.ENABLE_BREADCRUMBS)
            context['breadcrumbs'] = b
        
        context = loader.context(context, self.request)
        html = loader.mark_safe(loader.render(self.template_file,
                                              context))
        return self.http.HttpResponse(html,
                                      mimetype = 'text/html')
        
    def redirect(self, url):
        if self.is_xhr:
            return jredirect(url = url)
        else:
            return self.http.HttpResponseRedirect(url)
        
    def instancecode(self):
        '''If an instance is available, return a unique code for it. Otherwise return None.''' 
        instance = self.instance
        if not instance:
            return None
        appmodel = self.site.for_model(instance.__class__)
        if appmodel:
            return appmodel.instancecode(self.request, instance)
        else:
            return '%s:%s' % (instance._meta,instance.id)
    