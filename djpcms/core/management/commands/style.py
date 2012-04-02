'''Requires style
'''
import os
import logging
from optparse import make_option

import djpcms
from djpcms.utils.importer import import_module
from djpcms.style import css, cssv, dump_theme


LOGGER = logging.getLogger('style')


def render(site, theme, target, apps, mediaurl = None,
           show_variables = False):
    module = None
    applications = list(apps or site.settings.INSTALLED_APPS) 
    imported = {}
    mediaurl = mediaurl or site.settings.MEDIA_URL
    if site.settings.SITE_MODULE not in applications:
        applications.append(site.settings.SITE_MODULE)
    # Import applications styles if available
    for app in applications:
        modname = '{0}.style'.format(app)
        if modname in imported:
            continue
        try:
            imported[modname] = import_module(modname) 
            LOGGER.info('Successfully imported style from "{0}".'\
                        .format(modname))
        except ImportError as e:
            LOGGER.warn('Cannot import application {0}: "{1}"'\
                        .format(app,e))
    #mediaurl = mediaurl
    dump_theme(theme, target, show_variables = show_variables)


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
    
    def handle(self, options):
        site = self.website()
        target = options.file
        mediaurl = options.mediaurl
        apps = options.apps
        self.theme = options.theme or site.settings.STYLING
        if not target:
            target = '{0}.css'.format(self.theme)
            mdir = os.path.join(site.settings.SITE_DIRECTORY,
                                'media',
                                site.settings.SITE_MODULE)
            if os.path.isdir(mdir):
                target = os.path.join(mdir, target)
        self.target = target
        djpcms.init_logging(site.settings)
        render(site, self.theme, self.target, apps, mediaurl, options.variables)
        
        
        