from .profiler import profile_response
from .wrappers import Request, Response
from .cache import djpcmsinfo


DJPCMS = 'DJPCMS'


__all__ = ['WSGI','WSGIsite']
    

class BaseSiteHandler(object):
    
    def __init__(self, site):
        self.site = site
        self.handle_exception = site.handle_exception
        self.root = self.site.root
    
    def get_request(self, environ, site = None):
        if DJPCMS not in environ:
            environ[DJPCMS] = djpcmsinfo(None,None,site=site)
        return Request(environ)
    
    
def response_error(f):
    
    def _(self, environ, start_response):
        site = self.site
        try:
            return f(self, environ, start_response)
        except Exception as e:
            site = getattr(e,'site',None)
            return self.handle_exception(self.get_request(environ,site), e)
    
    return _
    
    
class WSGI(BaseSiteHandler):
    '''WSGI handler. It looks for application sites and
delegate the handling to them.'''
    def __call__(self, environ, start_response):
        self.root.request_started.send(self, environ = environ)
        if self.root.settings.PROFILING_KEY:
            response = profile_response(environ, start_response,
                                        self.root.settings.PROFILING_KEY,
                                        self._handle,
                                        self.site.settings)
        else:
            response = self._handle(environ, start_response)
        res = response(environ, start_response)
        self.root.request_finished.send(self, environ = environ)
        return res
        
    @response_error
    def _handle(self, environ, start_response):
        cleaned_path = self.site.clean_path(environ)
        if cleaned_path:
            return cleaned_path
        appsite,view,kwargs = self.site.resolve(environ['PATH_INFO'][1:])
        environ[DJPCMS] = djpcmsinfo(view,kwargs)
        return appsite.handle(environ, start_response)
            
    
class WSGIsite(BaseSiteHandler):
    '''Box standard wsgi response handler'''
    @response_error
    def __call__(self, environ, start_response):
        request = self.get_request(environ)
        info = request.DJPCMS
        site = info.site
        response = info.djp(request)
        if not isinstance(response,Response):
            djp = response
            response = None
            info.page = djp.page
            #signals.request_started.send(sender=self.__class__)
            # Request middleware
            for middleware_method in site.request_middleware():
                response = middleware_method(request)
                if response:
                    break
                
            if response is None:
                self.root.start_response.send(sender=self.__class__,
                                              request=request)
                response = djp.response()
            
                # Response middleware
                for middleware_method in site.response_middleware():
                    response = middleware_method(request,response)
            
        return response
    

