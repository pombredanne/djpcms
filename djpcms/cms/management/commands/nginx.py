import os
import platform

from djpcms import cms
from djpcms.apps.static.utils import nginx_reverse_proxy_config 


class Command(cms.Command):
    option_list = (
        cms.CommandOption('nginx',('-n','--nginx'),
                default='http://{0}'.format(platform.node()),
                description='Nginx server as http://host or https://host.'),
        cms.CommandOption('port',('-p','--nginx-port'),
                type=int, default=80,
                description='Nginx server port.'),
        cms.CommandOption('server',('-s','--server'),
                default='http://127.0.0.1:8060',
                description='Python server as http://host:port.'),                                                                       
        cms.CommandOption('target',('-t','--target'),
                default='',
                description='Target path of nginx config file.'),
        cms.CommandOption('enabled',('-e','--enabled'),
                action = 'store_true',
                default = False,
                description='Save the file in the nginx\
 /etc/nginx/sites-enabled directory.'),
    )
    help = "Creates a nginx config file for a reverse-proxy configuration."
    
    def handle(self, options, target=None):
        target = target if target is not None else options.target
        nginx_server = '{0}:{1}'.format(options.nginx, options.port)
        path = None
        if options.enabled and os.name == 'posix':
            path = '/etc/nginx/sites-enabled'
        site = self.website(options)
        target = nginx_reverse_proxy_config(site,
                                            nginx_server,
                                            proxy_server=options.server,
                                            target=target,
                                            path=path).save()
        self.logger.info('Created nginx configuration file "%s"', target)
        self.logger.info('You need to restart nginx.')
        self.logger.info('in linux /etc/init.d/nginx restart')
        
        
        