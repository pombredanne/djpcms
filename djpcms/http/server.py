import logging
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler

from .handlers import WSGI

__all__ = ['serve']


class wsgi(object):
    
    def __init__(self, middleware):
        self.middleware = middleware
        
    def __call__(self, environ, start_response):
        '''The WSGI callable'''
        #request = self.REQUEST(environ)
        for middleware in self.middleware:
            response = middleware(environ, start_response)
            if response is not None:
                return response
        return ()


def serve(sites_factory, port = 0, use_reloader = False):
    """Create a new WSGI server listening on `host` and `port` for `app`"""
    log = logging.getLogger()
    server = WSGIServer(('', port), WSGIRequestHandler)
    server.set_app(wsgi(sites_factory.wsgi_middleware()))
    log.info('Serving on port {0}'.format(port))
    server.serve_forever()