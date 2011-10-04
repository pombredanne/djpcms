import logging
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler

from .handlers import WSGI

__all__ = ['serve']


def serve(port = 0, sites = None, use_reloader = False):
    """Create a new WSGI server listening on `host` and `port` for `app`"""
    log = logging.getLogger()
    server = WSGIServer(('', port), WSGIRequestHandler)
    server.set_app(WSGI(sites))
    log.info('Serving on port {0}'.format(port))
    server.serve_forever()