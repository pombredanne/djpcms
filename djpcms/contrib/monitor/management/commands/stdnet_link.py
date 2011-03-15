import os
import logging
from optparse import make_option

from djpcms import sites
from djpcms.apps.management.base import BaseCommand
from djpcms.contrib.monitor import linked

from stdnet.orm import register_applications

logger = logging.getLogger('djpcms.execute.stdnet_link')

class Command(BaseCommand):
    help = "Syncronize stdnet and other orm models linked."
    args = '[appname appname.Modelname ...]'
    
    def handle(self, *args, **options):
        sites.load()
        settings = sites.settings
        apps = set(args)
        for model in linked(settings.INSTALLED_APPS):
            modname = str(model._meta)
            appname = model._meta.app_label
            if not args or appname in args or modname in args:
                djmodel = model._meta.linked
                logger.info('Synching model {0} with django\
 model {1}'.format(model._meta,djmodel._meta))
                model.objects.synch()