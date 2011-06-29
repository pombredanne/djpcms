from datetime import date, datetime
from inspect import isclass

from djpcms.utils.text import nicename
from djpcms.utils.dates import smart_time
from djpcms.utils.const import EMPTY_VALUE, EMPTY_TUPLE, SLASH, DIVEND, SPANEND, NOTHING
from djpcms.utils import force_str, mark_safe, significant_format
from djpcms.utils import escape as default_escape

from .icons import yes,no
from .widgets import CheckboxInput
from .apptools import table_header


__all__ = ['nicerepr',
           'field_repr',
           'results_for_item',
           'nice_headers',
           'table_checkbox',
           'NONE_VALUE']

FIELD_SPLITTER = '__'
NONE_VALUE = '(None)'
divchk = '<div class="action-check">'
spvval = '<span class="value">'


def table_checkbox(val,id):
    if val:
        chk = CheckboxInput(name = 'action-item', value = id).render()
        val = divchk+chk+spvval+val+SPANEND+DIVEND
    return mark_safe(val)


def nicerepr(val,
             nd = 3,
             none_value = NONE_VALUE,
             dateformat = None,
             timeformat = None,
             **kwargs):
    '''\
Prettify a value to be displayed in html.
    
:parameter val: value to prettify.
:parameter nd: numerical accuracy for floating point numbers.
'''
    if val is None:
        return NONE_VALUE
    elif isinstance(val,datetime):
        return smart_time(val,dateformat,timeformat)
    elif isinstance(val,bool):
        if val:
            return yes()
        else:
            return no()
    else:
        try:
            return significant_format(val, n = nd)
        except TypeError:
            return force_str(val)
    
    
def field_repr(field_name, obj, appmodel = None, **kwargs):
    '''Retrive the value of attribute *field_name*
from an object *obj* by trying out
several possibilities in the following order.

* If *field_name* is not defined or empty it returns ``None``.
* If *field_name* is an attribute of *obj* it returns the value.
* If *obj* is a dictionary type object and *field_value* is in *obj* it returns the vaue.
* If *appmodel* is defined it invokes the
  :meth:`djpcms.views.Application.get_intance_value`
* Return ``None``
'''
    if not field_name:
        val = None
    elif hasattr(obj,field_name):
        try:
            val = getattr(obj,field_name)
            if not isclass(val) and hasattr(val,'__call__'):
                val = val()
        except Exception as e:
            val = str(e)
    elif hasattr(obj,'__getitem__') and field_name in obj:
        val = obj[field_name]
    elif FIELD_SPLITTER in field_name:
        fnames = field_name.split(FIELD_SPLITTER)
        if hasattr(obj,fnames[0]):
            field = getattr(obj,fnames[0])
            return field_repr(FIELD_SPLITTER.join(fnames[1:]), field, **kwargs)
        elif appmodel:
            val = appmodel.get_intance_value(obj, field_name)
        else:
            val = None
    elif appmodel:
        val = appmodel.get_intance_value(obj, field_name)
    else:
        val = None
    return nicerepr(val,**kwargs)

    
def nice_headers(headers, mapper = None):
    if not mapper:
        return (nicename(name) for name in headers)
    else:
        return (mapper.label_for_field(name) for name in headers)
            
            
def results_for_item(djp, headers, result, appmodel = None, 
                     actions = None, **kwargs):
    '''Return an iterable over values in result given by attributes in headers.
    
:parameter headers: iterable over attribute names.
:parameter result: instance of obhject to estract attributes from.
:parameter appmodel: optional instance of :class:`djpcms.views.Application`.
'''
    if appmodel:
        getr = get_app_result(appmodel.mapper,actions)
        id = getr.id(result)
    else:
        id = None
        if hasattr(result,'__iter__'):
            getr = get_iterable_result(result)
        else:
            getr = get_result()
    return {'id': id,
            'display': (getr(djp.request,name,result,appmodel,**kwargs)\
                        for name in headers)}


class get_result(object):
    __slots__ = ('first',)
    def __init__(self):
        self.first = True

    def __call__(self, request, field_name, result, appmodel, **kwargs):
        return field_repr(field_name, result, appmodel = appmodel, **kwargs)
    
    
class get_iterable_result(object):
    
    def __init__(self, results):
        self.iter = iter(results)

    def __call__(self, request, field_name, result, appmodel, **kwargs):
        try:
            value = nicerepr(next(self.iter),**kwargs)
            return {'name':field_name,'value':value}
        except StopIteration:
            return None
        
    
class get_app_result(object):
    '''Representation for an instance field'''
    __slots__ = ('mapper','actions','first',)
    
    def __init__(self, mapper, actions = False):
        self.mapper = mapper
        self.actions = actions
        self.first = True
        
    def id(self, result):
        try:
            return self.mapper.unique_id(result)
        except:
            return None
    
    def __call__(self, request, head, result, appmodel,
                 nd = 3, path = None, escape = None, **kwargs):
        mapper = self.mapper
        first = self.first
        url = None
        if head:
            head = table_header(head)
            result_repr = field_repr(head.function, result,
                                     appmodel = appmodel, nd = nd)
            if(self.first and not appmodel.list_display_links) or \
                    head.code in appmodel.list_display_links:
                first = False
                url = appmodel.viewurl(request, result,
                                       field_name = head.code)
            
            var = result_repr
            if url:
                if url != path:
                    var = mark_safe('<a href="{0}" title="{1}">{1}</a>'.format(url, var))
                else:
                    var = mark_safe('<a>{0}</a>'.format(var))
        else:
            var = ''
        
        if self.first and self.actions:
            first = False 
            var = table_checkbox(var, getattr(result,'id',None))
        
        escape = escape or default_escape
        var = escape(var)
        self.first = first
        return {'name':head.code,
                'value':var}
    