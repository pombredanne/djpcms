import os
from optparse import make_option

from djpcms import sites, template
from djpcms.utils.importer import import_module
from djpcms.apps.management.base import BaseCommand

from medplate import rendercss

default_style = 'allwhite'


def render(style, target, apps, template_engine = None):
    module = None
    applications = apps or sites.settings.INSTALLED_APPS 
    imported = {}
    
    # Import applications styles if available
    for app in applications:
        modname = '{0}.style'.format(app)
        if modname in imported:
            continue
        try:
            imported[modname] = import_module(modname) 
            continue
        except ImportError:
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
    
    data = rendercss(style,
                     sites.settings.MEDIA_URL,
                     template_engine)
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
                    help='Target path of css file. For example media/site/site.css. If\
 not provided, a local file called style.css will be created.'),
        make_option('-a','--applications',
                    action='store',
                    dest='apps',
                    default='',
                    help='Target applications (space separated).\
 If not provided all applications will be processed.'),
    )
    help = "Creates a css file from a template css."
    
    def handle(self, *args, **options):
        style = options['style']
        target = options['target']
        apps = options['apps']
        if not target:
            target = 'style.css'
        if apps:
            apps = apps.split()
        else:
            apps = None
        render(style,target,apps)
        
        
        