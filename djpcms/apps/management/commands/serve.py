import os
from optparse import make_option

import djpcms
from djpcms.apps.management.base import BaseCommand
from djpcms.http import serve

DEFAULT_PORT = 8060


class Command(BaseCommand):
    option_list = BaseCommand.option_list
    help = "Serve the application."
    args = '[optional port number]'
    
    def handle(self, callable, *args, **options):
        sites = callable()
        if not sites:
            print('No sites installed, cannot serve the application')
            return
        
        if args:
            port = int(args[0])
        else:
            port = DEFAULT_PORT
        djpcms.init_logging(sites.settings)
        serve(port = port, sites = sites)
