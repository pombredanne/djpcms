from stdnet import orm
from djpcms.apps.management.base import BaseCommand

from monitor import installed_models                    

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-f','--format',
                     action='store',
                     dest='format',
                     default='json',
                     help='The data format.'),
    )
    help = "Flush stdnet models in the data-server."
    args = '[appname appname.ModelName ...]'
    
    def handle(self, callable, *args, **options):
        sites = callable()
        serializer = orm.get_serializer(options['format'])
        for model in installed_models(sites,args):
            qs = model.object.all().order_by('id')
            model.flush()
            print('flushed {0}'.format(model._meta))
