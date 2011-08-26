import os

from djpcms.template import loader
from djpcms.apps.included.static import application_map


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
        

class nginx_reverse_proxy(object):
    '''Nginx as reverse proxy for serving media files'''
    nginx = 'nginx.conf'
    default_parameters = {}
    
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
        if dir is None:
            dir = None if not release else environ['confdir']
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
        