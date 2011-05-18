from djpcms.apps.management.base import BaseCommand
from djpcms.contrib.monitor import installed_models                    

class Command(BaseCommand):
    help = "Flush stdnet models in the data-server."
    args = '[appname appname.ModelName ...]'
    
    def handle(self, callable, *args, **options):
        sites = callable()
        for model in installed_models(sites,args):
            model.flush()
            print('flushed {0}'.format(model._meta))
