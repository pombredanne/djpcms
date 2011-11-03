import os

import djpcms
from djpcms.http import serve

DEFAULT_PORT = 8060


class Command(djpcms.Command):
    help = "Serve the application."
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
