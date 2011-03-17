'''\
Utilities for displaying interactive table with pagination and actions.
'''
from djpcms.template import loader
from djpcms.core import orms
from djpcms.utils import force_str
from djpcms.utils.const import EMPTY_VALUE, EMPTY_TUPLE, SLASH, DIVEND, SPANEND
from djpcms.utils.text import nicename
from djpcms.html import icons

from .widgets import Select, CheckboxInput

nicerepr = orms.nicerepr

from .utils import LazyRender

__all__ = ['Table','table','nicerepr','table_checkbox']


def response_table_row(headers,item,path=SLASH):
    for field in headers:
        v = getattr(item,field,None)
        if hasattr(v,'__call__'):
            v = v()
        yield v
        

divchk = '<div class="action-check">'
spvval = '<span class="value">'

def table_checkbox(val):
    chk = CheckboxInput(value = val, name = 'action-item').render()
    if val:
        val = divchk+chk+spvval+val+SPANEND+DIVEND
    return val
        

class get_result(object):
    
    def __init__(self, actions = False):
        self.actions = actions
        self.first = True
        
    def __call__(self, field_name, result, mapper, nd):
        if not field_name:
            return EMPTY_VALUE
        result_repr = force_str(mapper.getrepr(field_name, result, nd))
        if result_repr == '':
            return EMPTY_VALUE
        else:
            return result_repr
    
class get_app_result(get_result):
    '''Representation for an instance field'''
        
    def __call__(self, request, field_name, result, mapper, nd, appmodel, path):
        first = self.first
        if field_name:
            result_repr = mapper.getrepr(field_name, result, nd)
            if force_str(result_repr) == '':
                result_repr = EMPTY_VALUE
            if(self.first and not appmodel.list_display_links) or \
                    field_name in appmodel.list_display_links:
                first = False
                url = appmodel.viewurl(request, result, field_name = field_name)
            else:
                url = None
            
            var = result_repr
            if url:
                if url != path:
                    var = '<a href="{0}" title="{1}">{1}</a>'.format(url, var)
                else:
                    var = '<a>{0}</a>'.format(var)
        else:
            var = ''
        if self.first and self.actions:
            first = False
            var = table_checkbox(var)
        self.first = first
        return var


def nice_items_id(headers, result, path, nd, id = None):
    if not hasattr(result,'__iter__'):
        result = response_table_row(headers,result,path)
    return {'id': id,
            'display': (nicerepr(c,nd) for c in result)}
    
    
def table_toolbox(appmodel, djp, headers):
    '''Create a toolbox for the table if possible'''
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
        s = Select(choices = choices, cn = 'ajax actions').addAttr('href',action_url)
        toolbox['actions'] = s.render(djp)
        toolbox['cols'] = len(headers)
    if addurl:
        toolbox['links'] = [icons.circle_plus(addurl,'add')]
    return toolbox
        
        
def result_for_item(djp, headers, result, nd,
                    mapper, appmodel, path,
                    actions = False):
    '''Return a dictionary containing a unique id and a
generator over values to display for each header value.
This function can be used to generate a row in table with entries given by
*headers*.

:parameter headers: iterable over attribute names to extract from ``result``.
:parameter result: the data element to process.
'''
    view = djp.view
    site = view.site
    if mapper and isinstance(result, mapper.model):
        request = djp.request
        if appmodel:
            #links = appmodel.object_links(mapper.model)
            getr = get_app_result(actions)
            display = (getr(request,name,result,mapper,nd,appmodel,path) for name in headers)
        else:
            getr = get_result(actions)
            display = (getr(name,result,mapper,nd) for name in headers)
        return {'id':mapper.unique_id(result),
                'display':display}
    else:
        return nice_items_id(headers, result, path, nd)


class Table(object):
    template_name = ('tablesorter.html',
                     'djpcms/tablesorter.html')
    
    def __init__(self, djp, headers, data, model = None,
                 nd = 3, template_name = None):
        '''\
Render a table

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
        if model:
            mapper = orms.mapper(model)
            appmodel = djp.view.site.for_model(model)
        else:
            mapper = None
            appmodel = None
        
        toolbox = None
        actions = False
        if appmodel:
            toolbox = table_toolbox(appmodel, djp, headers)
            actions = 'actions' in toolbox
            
        if not mapper:
            labels = (nicename(name) for name in headers)
        else:
            labels = (mapper.label_for_field(name) for name in headers)
        items  = (result_for_item(djp, headers, d, nd, mapper, appmodel,\
 path, actions = actions) for d in data)
        self.ctx = {'labels': labels,
                    'items': items,
                    'toolbox':toolbox}
            
    def render(self):
        return loader.render(self.template_name,self.ctx)


def table(djp, headers, data, model = None,
          nd = 3, template_name = None):
    t = Table(djp, headers, data, model, nd, template_name) 
    return LazyRender(t)
