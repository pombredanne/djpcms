"""
Management utility to re index stdnet search engine.
Requires stdnet.contrib.searchengine to be part of INSTALLED_APPS
"""
from djpcms.apps.management.base import BaseCommand
from djpcms.contrib.monitor import installed_models


class Command(BaseCommand):
    help = "Re-index search engine."
    args = '[appname appname.ModelName ...]'

    def handle(self, *args, **options):
        sites = callable()
        if 'stdnet.contrib.searchengine' not in sites.settings.INSTALLED_APPS:
            print('"stdnet.contrib.searchengine" must be in yout "INSTALLED_APPS" list to use this command.')
            exit(0)
        if not args:
            
        for model in installed_models(sites,args):
            pass
