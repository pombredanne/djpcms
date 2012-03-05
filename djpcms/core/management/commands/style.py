import os
from optparse import make_option

import djpcms
from djpcms.utils.importer import import_module
from djpcms.style import css, cssv


def render(sites, theme, target, apps, mediaurl = None,
           show_variables = False):
    module = None
    applications = apps or sites.settings.INSTALLED_APPS 
    imported = {}
    mediaurl = mediaurl or sites.settings.MEDIA_URL
    site = sites[0]
    # Import applications styles if available
    for app in applications:
        modname = '{0}.style'.format(app)
        if modname in imported:
            continue
        try:
            imported[modname] = import_module(modname) 
            print('Successfully imported style from "{0}".'.format(modname))
        except ImportError as e:
            print('NOTE: Cannot import application {0}: "{1}"'\
                        .format(app,e))
            pass
            
    #import site style if available
    if not apps:
        modname = '{0}.style'.format(sites.settings.SITE_MODULE)
        if modname not in imported:
            try:
                import_module(modname)
                print('Successfully imported style from {0}.'.format(modname))
            except:
                pass
    # set the theme
    cssv.set_theme(theme)
    if show_variables:
        print('STYLE: {0}'.format(variables.theme))
        section = None
        for var in variables:
            sec = var.name.split('_')[0]
            if sec != section:
                section = sec
                print('')
                print(section)
                print('==================================================')
            print('{0}: {1}'.format(var.name,var.value))
    else:
        data = css.render(mediaurl)
        f = open(target,'w')
        f.write(data)
        f.close()
        print('Saved style on file "{0}"'.format(target))


class Command(djpcms.Command):
    help = "Creates a css file from a template css."
    option_list = (
                   djpcms.CommandOption('apps',nargs='*',
                        description='appname appname.ModelName ...'),
                   
                   djpcms.CommandOption('theme',('-t','--theme'),
                                default='',
                                description='Theme to use. For example smooth'),
                   djpcms.CommandOption('file',('-f','--file'),
                                default='',
                                description='Target path of css file.\
 For example "media/site/site.css". If not provided, a file called\
 {{ STYLE }}.css will\
 be created and put in "media/<sitename>" directory, if available,\
 otherwise in the local directory.'),
                   djpcms.CommandOption('mediaurl',('-m','--media'),
                                default='',
                                description='Specify the media url.\
 Override settings value.'),
                   djpcms.CommandOption('variables',('-v','--variables'),
                                action = 'store_true',
                                default = False,
                                description='List all variables values')
                   )
    
    def handle(self, sites_factory, options):
        theme = options.theme
        target = options.file
        mediaurl = options.mediaurl
        apps = options.apps
        sites = sites_factory()
        theme = theme or sites.settings.STYLING
        if not target:
            target = '{0}.css'.format(theme)
            mdir = os.path.join(sites.settings.SITE_DIRECTORY,
                                'media',
                                sites.settings.SITE_MODULE)
            if os.path.isdir(mdir):
                target = os.path.join(mdir, target)
        render(sites,theme,target,apps,mediaurl,options.variables)
        
        
        