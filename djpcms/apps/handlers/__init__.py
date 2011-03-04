from djpcms import sites
from djpcms.core.exceptions import PermissionDenied


class BaseSiteHandler(object):
    
    def __init__(self, site):
        self.site = site
        self.handle_exception = sites.handle_exception
        
    def __call__(self, environ, start_response):
        return self._handle_response(environ, start_response)
    
    def _handle_response(self, environ, start_response):
        raise NotImplementedError
    
    
class DjpCmsHandler(BaseSiteHandler):
    '''Base DjpCms wsgi handler. It looks for application sites and
delegate the handling to them.'''
    def __init__(self):
        from djpcms import sites
        super(DjpCmsHandler,self).__init__(sites)
        
    def _handle_response(self, environ, start_response):
        site = self.site
        site.load()
        http = site.http
        try:
            cleaned_path = site.clean_path(environ)
            if isinstance(cleaned_path,http.HttpResponse):
                return cleaned_path
            application = site.get_site(environ['PATH_INFO'][1:])
        except Exception as e:
            request = http.make_request(environ)
            request.site = site
            res = self.handle_exception(request, e)
        else:
            res = application.handle(environ, start_response)
        return http.finish_response(res, environ, start_response)
            
    
class WSGI(BaseSiteHandler):
    '''Box standard wsgi response handler'''
    def _handle_response(self, environ, start_response):
        site = self.site
        http = site.http
        HttpResponse = http.HttpResponse
        response = None
        path     = environ['PATH_INFO']
        try:
            request = http.make_request(environ)
            request.site = site
            site,view,kwargs = site.resolve(path[1:])
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
        except PermissionDenied as e:
            return self.handle_exception(request, e, status = 403)
        except http.Http404 as e:
            return self.handle_exception(request, e, status = 404)
        except http.HttpException as e:
            return self.handle_exception(request, e, status = e.status)
        except Exception as e:
            return self.handle_exception(request, e)


class WebSocketWSGI(object):
    
    def _handle_response(self, environ, start_response):
        raise NotImplementedError
    
    