try:
    input = raw_input
except NameError:
    pass

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
        models = list(installed_models(sites,options.apps))
        if models:
            print('')
            print('Are you sure you want to remove these models?')
            print('')
            for model in models:
                print('{0} from {1}'.format(model,
                                            model._meta.connection_string))
            print('')
            yn = input('yes/no : ')
            if yn.lower() == 'yes':
                for model in models:
                    N = model.flush()
                    print('{0} - removed {1} keys'.format(model,N))
            else:
                print('Nothing done.')
        else:
            print('Nothing done. No models selected')
