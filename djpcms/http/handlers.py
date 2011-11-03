from .profiler import profile_response
from .wrappers import Request, Response
from .cache import djpcmsinfo


DJPCMS = 'DJPCMS'


__all__ = ['WSGI']

    
class WSGI(object):
    '''WSGI handler. It looks for application sites and
delegate the handling to them.'''
    def __init__(self, sites):
        self.sites = sites
        
    def __call__(self, environ, start_response):
        settings = self.sites.settings
        if settings.PROFILING_KEY:
            response = profile_response(environ, start_response,
                                        self.sites,
                                        settings.PROFILING_KEY,
                                        self._handle,
                                        settings)
        else:
            response = self._handle(environ, start_response)
        return response
    
    def get_request(self, environ, site):
        if DJPCMS not in environ:
            environ[DJPCMS] = djpcmsinfo(None,None,site=site)
        return Request(environ)
        
    def _handle(self, environ, start_response):
        site = self.sites
        try: 
            cleaned_path = site.clean_path(environ)
            if cleaned_path:
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
        except Exception as e:
            return site.handle_exception(self.get_request(environ,site), e)
        
            