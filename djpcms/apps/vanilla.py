'''\
Dependcies: **None**

This is the plain vanilla of all applications. It has the standard five views

* search (:class:`djpcms.views.SearchView`)
* add (:class:`djpcms.views.AddView`)
* view (:class:`djpcms.views.ViewView`)
* change (:class:`djpcms.views.ChangeView`)
* delete (:class:`djpcms.views.DeleteView`)
'''
from djpcms import views, SLUG_REGEX


class SimpleTabular(views.ModelApplication):
    '''A very simple application for sdisplaying a table'''
    table_parameters = {'footer':False,
                        'data':{'options':{'sDom':'t'}}}
    table_actions = ()
    in_navigation = 0
    search = views.SearchView(astable = True)
    

class Application(views.ModelApplication):
    search = views.SearchView()
    add = views.AddView()
    view = views.ViewView()
    change = views.ChangeView()
    delete = views.DeleteView()
    
    
    
class GroupApplication(views.Application):
    '''An application group. NOT YET READ NOR TESTED'''
    home = views.View()
    search = views.SearchView(regex = SLUG_REGEX, parent = 'home')
    add = views.AddView()
    view = views.ViewView()
    change = views.ChangeView()
    delete = views.DeleteView()