import os
from optparse import make_option

import djpcms
from djpcms.apps.management.base import BaseCommand

DEFAULT_PORT = 8060

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-u','--using',
                     action='store',
                     dest='using',
                     default='',
                     help='HTTP library to use when serving the application.'),
    )
    help = "Serve the application."
    
    def handle(self, callable, *args, **options):
        if args:
            port = int(args[0])
        else:
            port = DEFAULT_PORT
        using = options['using']
        sites = callable()
        if not sites:
            print('No sites installed, cannot serve the aplication')
        elif using:
            sites.settings.HTTP_LIBRARY = using
        djpcms.init_logging(sites.settings)
        sites.http.serve(port = port, sites = sites)
