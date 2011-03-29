'''\
Utilities for displaying interactive table with pagination and actions.
'''
from djpcms.template import loader
from djpcms.utils.text import nicename
from djpcms.html import icons

from .nicerepr import *
from .widgets import Select

__all__ = ['Table']
    
    
def table_toolbox(djp, appmodel):
    '''\
Create a toolbox for the table if possible.

:parameter djp: an instance of a :class:`djpcms.views.DjpResponse`.
:parameter appmodel: an instance of a :class:`djpcms.views.Application`.
'''
    request = djp.request
    site = djp.site
    addurl = appmodel.addurl(djp.request)
    action_url = djp.url
    has = site.permissions.has
    choices = [('','Actions')]
    for name,description,pcode in appmodel.actions:
        if has(request, pcode, None):
            choices.append((name,description))
    toolbox = {}
    if len(choices) > 1:
        toolbox['actions'] = Select(choices).addData('url',action_url).render()
    if addurl:
        toolbox['links'] = [icons.circle_plus(addurl,'add')]
    return toolbox


class Table(object):
    template_name = ('tablesorter.html',
                     'djpcms/tablesorter.html')
    
    def __init__(self,
                 djp,
                 headers,
                 data,
                 model = None,
                 template_name = None,
                 paginator = None,
                 appmodel = None,
                 nd = 3):
        '''\
Render a table given a response object ``djp``.

:parameter djp: instance of :class:`djpcms.views.DjpResponse`.
:parameter headers: iterable over headers.
:parameter data: iterable over data to display.
:parameter model: optional model.
:parameter nd: numeric accuracy for floating point numbers.
:parameter template_name: template name
    '''
        self.template_name = template_name or self.template_name
        if not model:
            # try to get model from data
            try:
                model = data.model
            except AttributeError:
                pass
        path  = djp.http.path_with_query(djp.request)
        
        # model available
        if model:
            mapper = djp.mapper(model)
            appmodel = djp.view.site.for_model(model)
        else:
            appmodel = appmodel or djp.view.appmodel
            if appmodel:
                mapper = appmodel.mapper
            else:
                mapper = None
        
        toolbox = None
        actions = False
        if mapper:
            toolbox = table_toolbox(djp, appmodel)
            actions = 'actions' in toolbox
            
        items  = (results_for_item(djp, headers, d, appmodel,\
                                   mapper = mapper,\
                                   actions = actions,\
                                   nd = nd, path = path) for d in data)
        
        self.ctx = {'labels': nice_headers(headers,mapper),
                    'items': items,
                    'toolbox':toolbox,
                    'paginator':paginator}
            
    def render(self):
        return loader.render(self.template_name,self.ctx)

