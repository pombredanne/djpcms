from djpcms import UnicodeMixin
from djpcms.core.exceptions import PermissionDenied


DJPCMS = 'DJPCMS'


class djpcmsinfo(UnicodeMixin):
    
    def __init__(self,view,kwargs,page=None,site=None,instance=None):
        self.view = view
        self.kwargs = kwargs if kwargs is not None else {}
        self.page = page
        self.instance = instance
        self.context_cache = None
        if view:
            self.site = view.site
        else:
            self.site = site
        
    def __unicode__(self):
        return '{0}, {1}, {2}, {3}'.format(self.site,self.view,self.page,self.kwargs)
    
    def djp(self, request = None):
        if self.view:
            return self.view(request, **self.kwargs)
    
    @property
    def root(self):
        return self.site.root
    
    @property
    def tree(self):
        return self.site.tree
    

class BaseSiteHandler(object):
    
    def __init__(self, site):
        self.site = site
        self.handle_exception = site.handle_exception
        self.root = self.site.root
        
    def __call__(self, environ, start_response):
        raise NotImplementedError
    
    def get_request(self, environ, site = None):
        request = self.site.http.make_request(environ)
        if DJPCMS not in environ:
            environ[DJPCMS] = djpcmsinfo(None,None,site=site)
        setattr(request,DJPCMS,environ[DJPCMS])
        return request            
    
    
def response_error(f):
    
    def _(self, environ, start_response):
        site = self.site
        http = site.http
        try:
            return f(self, environ, start_response)
        except Exception as e:
            site = getattr(e,'site',None)
            return self.handle_exception(self.get_request(environ,site), e)
    
    return _
    
    
class DjpCmsHandler(BaseSiteHandler):
    '''Base DjpCms wsgi handler. It looks for application sites and
delegate the handling to them.'''
    def __call__(self, environ, start_response):
        self.root.request_started.send(self, environ = environ)
        res = self._handle(environ, start_response)
        if DJPCMS in environ:
            site = environ[DJPCMS].site
        else:
            site = self.site
        res = site.http.finish_response(res, environ, start_response)
        self.root.request_finished.send(self, environ = environ)
        return res
        
    @response_error
    def _handle(self, environ, start_response):
        site = self.site
        self.site.load()
        http = self.site.http
        cleaned_path = site.clean_path(environ)
        if isinstance(cleaned_path,http.HttpResponse):
            return cleaned_path
        appsite,view,kwargs = site.resolve(environ['PATH_INFO'][1:])
        environ[DJPCMS] = djpcmsinfo(view,kwargs)
        return appsite.handle(environ, start_response)
            
    
class WSGI(BaseSiteHandler):
    '''Box standard wsgi response handler'''
    @response_error
    def __call__(self, environ, start_response):
        info = environ[DJPCMS]
        site = info.site
        http = site.http
        HttpResponse = http.HttpResponse
        response = None
        request = self.get_request(environ)
        djp = info.djp(request)
        if isinstance(djp,HttpResponse):
            return djp
        info.page = djp.page
        #signals.request_started.send(sender=self.__class__)
        # Request middleware
        for middleware_method in site.request_middleware():
            response = middleware_method(request)
            if response:
                return http.finish_response(response, environ, start_response)
        self.root.start_response.send(sender=self.__class__, request=request)
        response = djp.response()
        info.instance = djp.instance
        # Response middleware
        for middleware_method in site.response_middleware():
            middleware_method(request,response)
        return response
    

class WebSocketWSGI(object):
    
    def _handle_response(self, environ, start_response):
        raise NotImplementedError
    
    