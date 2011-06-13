'''\
Utilities for displaying interactive table with pagination and actions.
'''
from djpcms import http
from djpcms.template import loader
from djpcms.utils.text import nicename
from djpcms.html import icons

from .nicerepr import *
from .base import HtmlWidget
from .widgets import Select

__all__ = ['Table']
    
    
def table_toolbox(djp, appmodel):
    '''\
Create a toolbox for the table if possible. A toolbox is created when
an application based on database model is available.

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
    groups = appmodel.column_groups(djp)
    if groups:
        data = {}
        choices = []
        for name,headers in groups:
            data[name] = headers
            choices.append((name,name))
        s = Select(choices)
        for name,val in data.items():
            s.addData(name,val)
        toolbox['columnviews'] = s.render()
    return toolbox


class Table(object):
    template_name = ('tablesorter.html',
                     'djpcms/tablesorter.html')
    
    def __init__(self,
                 djp,
                 headers = None,
                 data = None,
                 model = None,
                 template_name = None,
                 paginator = None,
                 appmodel = None,
                 nice_headers_handler = None,
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
        path  = http.path_with_query(djp.request)
        
        # model available
        if model:
            mapper = djp.mapper(model)
            appmodel = djp.view.site.for_model(model)
        else:
            #appmodel = appmodel or djp.view.appmodel
            if appmodel:
                mapper = appmodel.mapper
            else:
                mapper = None
        
        toolbox = None
        actions = False
        if appmodel:
            toolbox = table_toolbox(djp, appmodel)
            actions = 'actions' in toolbox
            
        items  = (results_for_item(djp, headers, d, appmodel,\
                                   mapper = mapper,\
                                   actions = actions,\
                                   nd = nd, path = path) for d in data)
        
        nice_headers_handler = nice_headers_handler or nice_headers 
        self.ctx = {'headers': list(self.headers(headers)),
                    'items': items,
                    'toolbox':toolbox,
                    'paginator':paginator}
            
    def headers(self, headers):
        '''Generator of hteml headers tags'''
        if isinstance(headers,dict):
            data = headers
        else:
            data = {}
        for head in headers:
            if head in data:
                inner,description = data[head]
            else:
                description = None
                inner = nicename(head)
            w = HtmlWidget('th', cn = head)
            if description:
                w.addData('description',description)
            yield w.render(inner = inner)
            
    def render(self):
        return loader.render(self.template_name,self.ctx)

