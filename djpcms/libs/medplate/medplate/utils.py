import os

import djpcms
from djpcms.template import loader
from djpcms.apps.included.static import application_map

if djpcms.ispy3k:
    from urllib.parse import urlparse
else:
    from urlparse import urlparse


def config_file(self, fname, ctx, dir = None):
    '''Create a configuration file from template and return the filename
* *fname*: The template used to create the file
* *dir*: directory containing the file or None. If none no file will be saved.
'''
    template = os.path.join('medplate',fname)
    data = loader.render(template,ctx)
    if dir:
        filename = config_file_name(fname, ctx)
        fullpath = os.path.join(dir,filename)
        f = open(fullpath,'w')
        f.write(data)
        f.close()
        return filename
    else:
        return data
        

class nginx_reverse_proxy_config(object):
    '''Nginx as reverse proxy for serving media files'''
    template = 'medplate/servers/nginx.conf_t'
    default_parameters = {}
    
    def __init__(self, appname, applications, target = None,
                 server = 'http://localhost:8060',
                 server_port = None, logdir = None,
                 redirects = None):
        if not target:
            target = '{0}_nginx.conf'.format(appname)
        if appname not in applications:
            raise djpcms.ImproperlyConfigured('Application name must be\
 in applications list')
        self.data = None
        sp = urlparse(server)
        loc = sp.netloc.split(':')
        if len(loc) == 2:
            host = loc[0]
            port = int(loc[1])
        else:
            raise djpcms.ImproperlyConfigured(
                        'Provide the server as http://host:port')
        secure = sp.scheme.lower() == 'https'
        default_server_port = 443 if secure else 80
        server_port = server_port or default_server_port
        server_port_for_host = ''
        if server_port != default_server_port:    
            server_port_for_host = ':{0}'.format(server_port)
        
        self.params = self.default_parameters.copy()
        self.params['server_port_for_host'] = server_port_for_host 
        self.params['secure'] = secure
        self.params['server_port'] = server_port
        self.params['port'] = port
        self.params['logdir'] = logdir
        apps = application_map(applications, safe=False)
        self.params['apps'] = apps.values()
        self.params['site'] = apps[appname]
        self.target = target or 'nginx.conf'
        redirects = redirects or []
        dnss = [host] + redirects
        ndns = [r.replace('.','\.') for r in dnss]
        self.params['dns'] = host
        self.params['redirects'] = redirects
        self.params['all_redirects'] = '|'.join(ndns)
    
    def write(self):
        if not self.data:
            self.data = loader.render(self.template,
                                      self.params)
            f = self.target
            if not hasattr(f,'write'):
                self.target = os.path.abspath(self.target)
                f = open(self.target,'w')
            f.write(self.data)
            self.file = f
        return self.file
        
    def save(self):
        f = self.write()
        f.close()
        self.data = None
    
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
        environ['nginx'] = self.config_file(self.nginx,ctx,dir=dir)
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
        