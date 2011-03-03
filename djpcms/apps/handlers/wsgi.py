
from .base import BaseSiteHandler



class WSGI(BaseSiteHandler):
    
    
    def __call__(self, environ, start_response):
        http = self.http
        HttpResponse = http.HttpResponse
        response = None
        site = None
        try:
            cleaned_path = self.clean_path(environ)
            if isinstance(cleaned_path,HttpResponse):
                return http.finish_response(cleaned_path, environ, start_response)
            path = cleaned_path[1:]
            request = http.make_request(environ)
            request.site = site
            site,view,kwargs = self.resolve(path)
            request.site = site
            post = request.form
            djp = view(request, **kwargs)
            if not isinstance(djp,HttpResponse):
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
            else:
                response = djp
        except PermissionDenied as e:
            response = self.handle_exception(self, request, e, status = 403)
        except http.Http404 as e:
            response = self.handle_exception(self, request, e, status = 404)
        except http.HttpException as e:
            response = self.handle_exception(self, request, e, status = e.status)
        except Exception as e:
            response = self.handle_exception(self, request, e)