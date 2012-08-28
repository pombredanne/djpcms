import os

from djpcms.apps.static import application_map
from djpcms.utils.httpurl import urlparse
    
    
def server_info(server):
    sp = urlparse(server)
    loc = sp.netloc.split(':')
    host = loc[0]
    if len(loc) == 2:
        port = int(loc[1])
    else:
        port = None
    secure = sp.scheme.lower() == 'https'
    default_server_port = 443 if secure else 80
    port = port or default_server_port
    if port != default_server_port:
        host_header = '$host:{0}'.format(port)
    else:
        host_header = '$host'
    return {'name':host,
            'port':port,
            'host_header': host_header, 
            'secure':secure}
    

class nginx_reverse_proxy_config(object):
    '''Create an nginx configuration file for serving
a python server behind nginx which acts as a reverse proxy for
serving media files.

:parameter site: the instance of :class:`djpcms.Site` which serve your
    application. 
:parameter nginx_server: the domain name for the server.
    This must be a fully qualified domain name.
:parameter proxy_server: the server running your application.
'''
    template_file = 'medplate/servers/nginx.conf_t'
    default_parameters = {}
    
    def __init__(self, site, nginx_server,
                 target = None,
                 proxy_server = 'http://localhost:8060',
                 logdir = None, redirects = None,
                 path = None):
        self.site = site
        self.settings = site.settings
        if not target:
            target = '{0}_nginx.conf'.format(self.settings.SITE_MODULE)
            if path:
                target = os.path.join(path,target)
        self.data = None
        self.params = params = {}
        params['nginx_server'] = server_info(nginx_server)
        proxy = server_info(proxy_server)
        params['secure'] = secure = proxy.pop('secure')
        if secure != params['nginx_server'].pop('secure'):
            raise valueError('nginx and proxy server have conflicting http')
        params['proxy_server'] = proxy_server
        params['logdir'] = logdir
        apps = application_map(self.settings.INSTALLED_APPS, safe=False)
        params['applications'] = apps.values()
        self.target = target or 'nginx.conf'
        params['redirects'] = redirects or []
        params['site'] = apps[self.settings.SITE_MODULE] 
        #dnss = [host] + redirects
        #ndns = [r.replace('.','\.') for r in dnss]
        #self.params['dns'] = host
        #self.params['redirects'] = redirects
        #self.params['all_redirects'] = '|'.join(ndns)
    
    def write(self):
        if not self.data:
            self.data = self.site.template.render(self.template_file,
                                                  self.params)
            f = self.target
            if not hasattr(f, 'write'): #pragma    nocover
                self.target = os.path.abspath(self.target)
                f = open(self.target,'w')
            f.write(self.data)
            self.file = f
        return self.file
        
    def save(self):
        f = self.write()
        f.close()
        self.data = None
        return self.target
    
    def build(self):
        pass
                
    def get_context(self, context):
        p = self.default_parameters.copy()
        p.update(context)
        return p
    
    def config_files(self, site, context, dir = None, release = True):
        ctx = self.get_context(context)
        dns = [ctx['dns']] + ctx['redirects']
        ndns = [r.replace('.','\.') for r in dns]
        ser.all_redirects = '|'.join(ndns)
        ser.apps = application_map(site.settings.INSTALLED_APPS,
                                    safe=False).values()
        environ['nginx'] = config_file(self, self.nginx, ctx, dir=dir)
        if not release:
            from __builtin__ import globals
            g = globals()
            g['script_result'] = environ

    def install(self, release = True):
        from fabric.api import env, sudo
        self.config(release)
        if release:
            env.apache = config_file_name(self.apache,env)
            env.nginx = config_file_name(self.nginx,env)
            
            sudo('cp %(confdir)s/%(apache)s /etc/apache2/sites-available/' % env)
            try:
                sudo('rm /etc/apache2/sites-enabled/%(apache)s' % env)
            except:
                pass
            sudo('ln -s /etc/apache2/sites-available/%(apache)s /etc/apache2/sites-enabled/%(apache)s' % env)
            
            sudo('cp %(confdir)s/%(nginx)s /etc/nginx/sites-available/' % env)
            try:
                sudo('rm /etc/nginx/sites-enabled/%(nginx)s' % env)
            except:
                pass
            sudo('ln -s /etc/nginx/sites-available/%(nginx)s /etc/nginx/sites-enabled/%(nginx)s' % env)
            if env.get('server_user',None):
                sudo('chown %(server_user)s:%(server_group)s -R %(logdir)s' % env)
        else:
            self.result = script_result
        return self

    def reboot(self):
        from fabric.api import sudo
        sudo("/etc/init.d/nginx restart")
        sudo('/etc/init.d/apache2 restart')
        return self
        