import os
import logging
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler

import djpcms

DEFAULT_PORT = 8060

logger = logging.getLogger('djpcms.server')


def serve(sites_factory, port = 0, use_reloader = False):
    """Create a new WSGI server listening on `host` and `port` for `app`"""
    server = WSGIServer(('', port), WSGIRequestHandler)
    server.set_app(sites_factory.wsgi())
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
