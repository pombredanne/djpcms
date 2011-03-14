import os
from optparse import make_option

from djpcms import sites
from djpcms.apps.management.base import BaseCommand
from djpcms.contrib.monitor.utils import register_models

from stdnet.orm import register_applications


class Command(BaseCommand):
    help = "Flush models in the data-server."
    args = '[appname appname.ModelName ...]'
    
    def handle(self, *args, **options):
        settings = sites.settings
        if args:
            models = register_models(args, app_defaults = settings.DATASTORE)
        else:
            models = register_applications(settings.INSTALLED_APPS,
                                           app_defaults = settings.DATASTORE)
        for model in models:
            model.flush()