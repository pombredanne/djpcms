import os
import platform

import djpcms

from djpcms.apps.static.utils import nginx_reverse_proxy_config 


class Command(djpcms.Command):
    option_list = (
        djpcms.CommandOption('nginx',('-n','--nginx'),
                default='http://{0}'.format(platform.node()),
                description='Nginx server as http://host or https://host.'),
        djpcms.CommandOption('port',('-p','--nginx-port'),
                type=int, default=80,
                description='Nginx server port.'),
        djpcms.CommandOption('server',('-s','--server'),
                default='http://127.0.0.1:8060',
                description='Python server as http://host:port.'),                                                                       
        djpcms.CommandOption('target',('-t','--target'),
                default='',
                description='Target path of nginx config file.'),
        djpcms.CommandOption('enabled',('-e','--enabled'),
                action = 'store_true',
                default = False,
                description='Save the file in the nginx\
 /etc/nginx/sites-enabled directory.'),
    )
    help = "Creates a nginx config file for a reverse-proxy configuration."
    
    def handle(self, sites_factory, options):
        target = options.target
        nginx_server = '{0}:{1}'.format(options.nginx,options.port)
        path = None
        if options.enabled and os.name == 'posix':
            path = '/etc/nginx/sites-enabled'
        sites = sites_factory()
        target = nginx_reverse_proxy_config(\
                        sites,
                        nginx_server,
                        proxy_server = options.server,
                        target = target,
                        path = path).save()
        print('Created nginx configuration file "{0}"'.format(target))
        print('You need to restart nginx.')
        print('in linux /etc/init.d/nginx restart')
        
        
        