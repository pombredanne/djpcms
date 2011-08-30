import os
from optparse import make_option

from djpcms.apps.management.base import BaseCommand

from medplate.utils import nginx_reverse_proxy_config 


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-p','--port',
                    type = int,
                    action="store",
                    dest='server_port',
                    default=0,
                    help='Nginx port.'),     
        make_option('-s','--server',
                    action="store",
                    dest='server',
                    default='http://localhost:8060',
                    help='Python server as http://host:port.'),                                                                       
        make_option('-t','--target',
                    action='store',
                    dest='target',
                    default='',
                    help='Target path of nginx config file.'),
    )
    help = "Creates a nginx config file for a reverse-proxy configuration."
    
    def handle(self, callable, *args, **options):
        if args:
            raise ValueError('Unknown arguments {0}'.format(', '.format(args)))
        target = options['target']
        sites = callable()
        target = nginx_reverse_proxy_config(\
                        sites.settings.SITE_MODULE,
                        sites.settings.INSTALLED_APPS,
                        target = target,
                        server = options['server'],
                        server_port = options['server_port']).save()
        print('Created nginx configuration file "{0}"'.format(target))
        
        
        