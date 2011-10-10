import djpcms

from monitor import installed_models                    

class Command(djpcms.Command):
    help = "Flush stdnet models in the data-server."
    option_list = (
                   djpcms.CommandOption('apps',nargs='*',
                        description='appname appname.ModelName ...'),
                   )
    
    def handle(self, callable, options):
        sites = callable()
        for model in installed_models(sites,options.apps):
            model.flush()
            print('flushed {0}'.format(model._meta))
