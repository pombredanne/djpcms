import logging
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler

from .handlers import DjpCmsHandler

__all__ = ['serve']


def serve(port = 0, sites = None, use_reloader = False):
    """Create a new WSGI server listening on `host` and `port` for `app`"""
    log = logging.getLogger()
    server = WSGIServer(('', port), WSGIRequestHandler)
    app = DjpCmsHandler(sites)
    server.set_app(app)
    log.info('Serving on port {0}'.format(port))
    server.serve_forever()