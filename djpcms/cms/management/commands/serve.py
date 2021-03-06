import os
import logging
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler

from djpcms import cms
from djpcms.utils.log import dictConfig

DEFAULT_PORT = 8060

LOGGER = logging.getLogger('djpcms.server')


def serve(site_factory, port=0, use_reloader=False, dry=False):
    """Create a new WSGI server listening on `host` and `port` for `app`"""
    server = WSGIServer(('', port), WSGIRequestHandler)
    server.set_app(site_factory.wsgi())
    LOGGER.info('Serving on port {0}'.format(port))
    if not dry:     #pragma nocover
        server.serve_forever()


class Command(cms.Command):
    help = "Serve the application using WSGIserver from the standard library."
    option_list = (
       cms.CommandOption(
            'port',
            nargs='?',
            type=int,
            default=DEFAULT_PORT,
            description='Optional port number'),
       cms.CommandOption(
            'dryrun',
            ('--dryrun',),
            action = 'store_true',
            default = False,
            description='Run the command without actually starting the server')
    )

    def handle(self, options):
        site = self.website(options)
        serve(self._website, port=options.port, dry=options.dryrun)

    def setup_logging(self, settings, options):
        LOGGING = settings.LOGGING
        if LOGGING:
            if settings.DEBUG:
                handlers = ['console']
                LOGGING['handlers']['console']['level'] = 'DEBUG'
                LOGGING['root'] = {
                                'handlers': handlers,
                                'level': 'DEBUG',
                                }
            dictConfig(settings.LOGGING)

