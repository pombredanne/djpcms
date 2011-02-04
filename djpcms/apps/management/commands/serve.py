import os
from optparse import make_option

from djpcms import sites
from djpcms.apps.management.base import BaseCommand

DEFAULT_PORT = 8060

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-u','--using',
                     action='store',
                     dest='using',
                     default='simple',
                     help='HTTP library to use when serving the application.'),
    )
    help = "Serve the application."
    
    def handle(self, *args, **options):
        if args:
            port = int(args[0])
        else:
            port = DEFAULT_PORT
        using = options['using']
        if not sites:
            print('No sites installed, cannot serve the aplication')
        else:
            sites.settings.HTTP_LIBRARY = using
            from djpcms import http
            http.serve(port = port)