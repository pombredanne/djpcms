'''Requires style
'''
import os
import logging
from optparse import make_option

from djpcms import cms
from djpcms.utils.importer import import_module
from djpcms.media.style import css, cssv, dump_theme


def render(site, theme, target, apps, mediaurl=None, show_variables=False):
    LOGGER = logging.getLogger('djpcms.command.style')
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
            # We need to check if the fily actually exists
            log = False
            try:
                appm = import_module(app)
            except ImportError:
                log = True
            else:
                path = getattr(appm, '__path__', None)
                if path:
                    pdir = os.path.join(path[0], 'style')
                    pfil = pdir + '.py'
                    if os.path.exists(pdir) or os.path.exists(pfil):
                        log = True
            if log:  
                LOGGER.error('Cannot import application {0}: "{1}"'\
                            .format(app,e))
    #mediaurl = mediaurl
    dump_theme(theme, target, show_variables=show_variables)


class Command(cms.Command):
    help = "Creates a css file from a template css."
    option_list = (
                   cms.CommandOption('apps',nargs='*',
                        description='appname appname.ModelName ...'),
                   cms.CommandOption('theme',('-t','--theme'),
                                default='',
                                description='Theme to use. For example smooth'),
                   cms.CommandOption('file',('-f','--file'),
                                default='',
                                description='Target path of css file.\
 For example "media/site/site.css". If not provided, a file called\
 {{ STYLE }}.css will\
 be created and put in "media/<sitename>" directory, if available,\
 otherwise in the local directory.'),
                   cms.CommandOption('mediaurl',('-m','--media'),
                                default='',
                                description='Specify the media url.\
 Override settings value.'),
                   cms.CommandOption('variables',('-v','--variables'),
                                action = 'store_true',
                                default = False,
                                description='List all variables values')
                   )
    
    def handle(self, options):
        site = self.website(options)
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
        render(site, self.theme, self.target, apps, mediaurl, options.variables)
        
        
        