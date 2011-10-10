from stdnet import orm

import djpcms

from monitor import installed_models                    

class Command(djpcms.Command):
    option_list = (
            djpcms.CommandOption('apps',nargs='*',
                description='appname appname.ModelName ...'),
            djpcms.CommandOption('format',('-f','--format'),
                     default='json', help='The data format.'),
    )
    help = "Flush stdnet models in the data-server."
    args = '[appname appname.ModelName ...]'
    
    def handle(self, callable, options):
        sites = callable()
        serializer = orm.get_serializer(options.format)
        for model in installed_models(sites,options.apps):
            qs = model.object.all().order_by('id')
            model.flush()
            print('flushed {0}'.format(model._meta))
