import os
from optparse import make_option

from djpcms import template, init_logging
from djpcms.utils.importer import import_module
from djpcms.apps.management.base import BaseCommand

from medplate import rendercss


def render(sites, style, target, apps, mediaurl = None, template_engine = None):
    module = None
    applications = apps or sites.settings.INSTALLED_APPS 
    imported = {}
    mediaurl = mediaurl or sites.settings.MEDIA_URL
    
    # Import applications styles if available
    for app in applications:
        modname = '{0}.style'.format(app)
        if modname in imported:
            continue
        try:
            imported[modname] = import_module(modname) 
            continue
        except ImportError as e:
            print('NOTE: Cannot import application {0}. MESSAGE: {1}'\
                        .format(app,e))
            pass
        try:
            modname = 'djpcms.contrib.{0}.style'.format(app)
            imported[modname] = import_module(modname)
        except ImportError:
            pass
    
    #import site style if available
    if not apps:
        modname = '{0}.style'.format(sites.settings.SITE_MODULE)
        if modname not in imported:
            try:
                import_module(modname)
            except:
                pass
    
    data = rendercss(style,mediaurl,template_engine)
    f = open(target,'w')
    f.write(data)
    f.close()



class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-s','--style',
                     action='store',
                     dest='style',
                     default='',
                     help='Style to use. For example smooth.'),
        make_option('-t','--target',
                    action='store',
                    dest='target',
                    default='',
                    help='Target path of css file. For example\
 "media/site/site.css". If not provided, a file called {{ STYLE }}.css will\
 be created and put in "media/<sitename>" directory, if available,\
 otherwise in the local directory.'),
        make_option('-m','--media',
                    action='store',
                    dest='mediaurl',
                    default='',
                    help='Specify the media url. Override settings value.')
    )
    help = "Creates a css file from a template css."
    args = '[appname appname ...]'
    
    def handle(self, callable, *args, **options):
        style = options['style']
        target = options['target']
        mediaurl = options['mediaurl']
        apps = args
        sites = callable()
        style = style or sites.settings.STYLING
        if not target:
            target = '{0}.css'.format(style)
            mdir = os.path.join(sites.settings.SITE_DIRECTORY,
                                'media',
                                sites.settings.SITE_MODULE)
            if os.path.isdir(mdir):
                target = os.path.join(mdir,target)
        render(sites,style,target,apps,mediaurl)
        
        
        