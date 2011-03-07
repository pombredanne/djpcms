from djpcms import sites
from djpcms.core.exceptions import PermissionDenied


class BaseSiteHandler(object):
    
    def __init__(self, site):
        self.site = site
        self.http = site.http
        self.handle_exception = sites.handle_exception
        
    def __call__(self, environ, start_response):
        raise NotImplementedError
    
    def get_request(self, environ, site = None):
        request = self.http.make_request(environ)
        request.site = site if site is not None else self.site
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
    
    def __init__(self):
        super(DjpCmsHandler,self).__init__(sites)
        
    def __call__(self, environ, start_response):
        res = self._handle(environ, start_response)
        if 'site-view-kwargs' in environ:
            site = environ['site-view-kwargs'][0]
        else:
            site = self.site
        return site.http.finish_response(res, environ, start_response)
        
    @response_error
    def _handle(self, environ, start_response):
        sites.load()
        http = sites.http
        cleaned_path = sites.clean_path(environ)
        if isinstance(cleaned_path,http.HttpResponse):
            return cleaned_path
        appsite,view,kwargs = sites.resolve(environ['PATH_INFO'][1:])
        environ['site-view-kwargs'] = (appsite,view,kwargs)
        return appsite.handle(environ, start_response)
            
    
class WSGI(BaseSiteHandler):
    '''Box standard wsgi response handler'''
    @response_error
    def __call__(self, environ, start_response):
        site, view, kwargs = environ['site-view-kwargs']
        http = site.http
        HttpResponse = http.HttpResponse
        response = None
        path     = environ['PATH_INFO']
        request  = self.get_request(environ)
        djp = view(request, **kwargs)
        if isinstance(djp,HttpResponse):
            return djp
        #signals.request_started.send(sender=self.__class__)
        # Request middleware
        for middleware_method in site.request_middleware():
            response = middleware_method(request)
            if response:
                return http.finish_response(response, environ, start_response)
        response = djp.response()
        # Response middleware
        for middleware_method in site.response_middleware():
            middleware_method(request,response)
        return response
    

class WebSocketWSGI(object):
    
    def _handle_response(self, environ, start_response):
        raise NotImplementedError
    
    