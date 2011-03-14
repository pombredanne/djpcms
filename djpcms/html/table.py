from djpcms.template import loader
from djpcms.core import orms
from djpcms.utils import force_str
from djpcms.utils.const import EMPTY_VALUE, EMPTY_TUPLE, SLASH
from djpcms.utils.text import nicename

nicerepr = orms.nicerepr

from .lazy import LazyRender

__all__ = ['Table','table','nicerepr']


def response_table_row(headers,item,path=SLASH):
    for field in headers:
        v = getattr(item,field,None)
        if hasattr(v,'__call__'):
            v = v()
        yield v
        

class get_result(object):
    __slots__ = ['first']
    
    def __init__(self):
        self.first = True
        
    def __call__(self, field_name, result, mapper, nd):
        if not field_name:
            return EMPTY_VALUE
        result_repr = force_str(mapper.getrepr(field_name, result, nd))
        if result_repr == '':
            return EMPTY_VALUE
        else:
            return result_repr
    
class get_app_result(object):
    '''Representation for an instance field'''
    __slots__ = ['first']
    
    def __init__(self):
        self.first = True
        
    def __call__(self, request, field_name, result, mapper, nd, appmodel, path):
        if not field_name:
            return ''
        result_repr = mapper.getrepr(field_name, result, nd)
        if force_str(result_repr) == '':
            result_repr = EMPTY_VALUE
        if(self.first and not appmodel.list_display_links) or \
                field_name in appmodel.list_display_links:
            self.first = False
            url = None
        else:
            url = None
        
        var = result_repr
        if url:
            if url != path:
                var = '<a href="{0}" title="{1}">{1}</a>'.format(url, var)
            else:
                var = '<a>{0}</a>'.format(var)
        return var


def nice_items_id(headers, result, path, nd, id = None):
    if not hasattr(result,'__iter__'):
        result = response_table_row(headers,result,path)
    return {'id': id,
            'display': (nicerepr(c,nd) for c in result)}
    
    
def result_for_item(djp, headers, result, nd,
                    mapper, appmodel, path):
    '''Return a dictionary containing a unique id and a
generator over values to display for each header value.
This function generate a row in the table

:parameter result: the data element to process
'''
    view = djp.view
    site = view.site
    if mapper and isinstance(result, mapper.model):
        request = djp.request
        if appmodel:
            #links = appmodel.object_links(mapper.model)
            getr = get_app_result()
            display = (getr(request,name,result,mapper,nd,appmodel,path) for name in headers)
        else:
            getr = get_result()
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
            
        if not mapper:
            labels = (nicename(name) for name in headers)
        else:
            labels = (mapper.label_for_field(name) for name in headers)
        items  = (result_for_item(djp, headers, d, nd, mapper, appmodel, path) for d in data)
        self.ctx = {'labels': labels,
                    'items': items}
            
    def render(self):
        return loader.render(self.template_name,self.ctx)


def table(djp, headers, data, model = None,
          nd = 3, template_name = None):
    t = Table(djp, headers, data, model, nd, template_name) 
    return LazyRender(t)
