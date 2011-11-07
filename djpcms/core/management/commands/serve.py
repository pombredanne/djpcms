import os
import logging
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler

import djpcms

DEFAULT_PORT = 8060

logger = logging.getLogger('djpcms.server')


class WSGI(object):
    
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


def serve(sites_factory, port = 0, use_reloader = False):
    """Create a new WSGI server listening on `host` and `port` for `app`"""
    server = WSGIServer(('', port), WSGIRequestHandler)
    server.set_app(WSGI(sites_factory.wsgi_middleware(),
                        sites_factory.response_middleware()))
    logger.info('Serving on port {0}'.format(port))
    server.serve_forever()


class Command(djpcms.Command):
    help = "Serve the application using WSGIserver from the standard library."
    option_list = (
                   djpcms.CommandOption('port',nargs='?',type=int,
                                        default=DEFAULT_PORT,
                                        description='Optional port number'),
                   )
    
    def handle(self, sites_factory, options):
        sites = sites_factory()
        if not sites:
            print('No sites installed, cannot serve the application')
            return
        
        port = options.port
        djpcms.init_logging(sites.settings)
        serve(sites_factory, port = port)
