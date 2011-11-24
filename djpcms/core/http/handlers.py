from djpcms.core.exceptions import Http404

from .profiler import profile_response
from .wrappers import Request, ResponseRedirect
from .cache import djpcmsinfo


DJPCMS = 'DJPCMS'


__all__ = ['WSGI','WSGIhandler']


class WSGIhandler(object):
    
    def __init__(self, middleware, response_middleware = None):
        self.middleware = middleware
        self.response_middleware = response_middleware or []
        
    def __call__(self, environ, start_response):
        '''The WSGI callable'''
        #request = self.REQUEST(environ)
        for middleware in self.middleware:
            response = middleware(environ, start_response)
            if response is not None:
                for rm in self.response_middleware:
                    rm(environ, start_response, response)
                response(environ, start_response)
                return response
        return ()

    
class WSGI(object):
    '''WSGI handler. It looks for application sites and
delegate the handling to them.'''
    def __init__(self, sites):
        self.sites = sites
        
    @property
    def route(self):
        return self.sites.route
    
    def __str__(self):
        return self.route
    
    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__,self)
        
    def __call__(self, environ, start_response):
        settings = self.sites.settings
        if settings.PROFILING_KEY:
            return profile_response(environ, start_response,
                                        self.sites,
                                        settings.PROFILING_KEY,
                                        self._handle,
                                        settings)
        else:
            return self._handle(environ, start_response)
        return response
    
    def get_request(self, environ, site):
        if DJPCMS not in environ:
            environ[DJPCMS] = djpcmsinfo(None,None,site=site)
        return Request(environ)
        
    def _handle(self, environ, start_response):
        site = self.sites
        try: 
            cleaned_path = site.clean_path(environ)
            if cleaned_path is not None:
                return cleaned_path
            site,view,kwargs = site.resolve(environ['PATH_INFO'][1:])
            environ[DJPCMS] = info = djpcmsinfo(view,kwargs)
            request = self.get_request(environ,site)
            response = info.djp(request)
            if not hasattr(response,'status_code'):
                djp = response
                info.page = djp.page
                response = djp.response()
            return response
        except Http404 as e:
            if e.trypath:
                return ResponseRedirect(e.trypath)
            else:
                return self._handle_error(environ, site, e)
        except Exception as e:
            return self._handle_error(environ, site, e)
        
    def _handle_error(self, environ, site, e):
            site = getattr(e,'site',site) or site
            return site.handle_exception(self.get_request(environ,site), e)
        
            