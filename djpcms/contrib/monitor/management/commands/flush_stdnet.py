import os
from optparse import make_option

from djpcms.apps.management.base import BaseCommand
from djpcms.contrib.monitor.utils import register_models

from stdnet.orm import model_iterator


class Command(BaseCommand):
    help = "Flush stdnet models in the data-server."
    args = '[appname appname.ModelName ...]'
    
    def handle(self, callable, *args, **options):
        sites = callable()
        installed = sites.settings.INSTALLED_APPS
        args = args or installed
        for arg in args:
            argo = arg
            if arg not in installed:
                arg = 'djpcms.contrib.{0}'.format(arg)
            if arg in installed:
                for model in model_iterator(arg):
                    model.flush()
                    print('flushed {0}'.format(model._meta))
            else:
                print('Application {0} not available'.format(argo))