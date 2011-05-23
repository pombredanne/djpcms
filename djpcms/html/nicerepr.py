from datetime import date, datetime
from inspect import isclass

from djpcms.utils.text import nicename
from djpcms.utils.dates import format as date_format
from djpcms.utils.const import EMPTY_VALUE, EMPTY_TUPLE, SLASH, DIVEND, SPANEND, NOTHING
from djpcms.utils import force_str, mark_safe, significant_format
from djpcms.utils import escape as default_escape

from .icons import yes,no
from .widgets import CheckboxInput


__all__ = ['nicerepr',
           'field_repr',
           'results_for_item',
           'nice_headers',
           'table_checkbox',
           'NONE_VALUE']

NONE_VALUE = '(None)'
DEFAULT_DATE_FORMAT = 'd M y'
DEFAULT_DATETIME_FORMAT = DEFAULT_DATE_FORMAT + ' H:i'

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
             dateformat = DEFAULT_DATE_FORMAT,
             datetime_format = DEFAULT_DATETIME_FORMAT,
             **kwargs):
    '''\
Prettify a value to be displayed in html.
    
:parameter val: value to prettify.
:parameter nd: numerical accuracy for floating points.
'''
    if val is None:
        return NONE_VALUE
    elif isinstance(val,datetime):
        time = val.time()
        if not time:
            return date_format(val.date(),dateformat)
        else:
            return date_format(val,datetime_format)
    elif isinstance(val,date):
        return date_format(val,dateformat)
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
    '''Retrive a field value from an object'''
    if not field_name:
        val = None
    elif hasattr(obj,field_name):
        try:
            val = getattr(obj,field_name)
            if not isclass(val) and hasattr(val,'__call__'):
                val = val()
        except Exception as e:
            val = str(e)
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
            
            
def results_for_item(djp, headers, result,
                     appmodel = None, mapper = None,
                     actions = None, **kwargs):
    '''Return an iterable over values in result given by attributes in headers.
    
:parameter headers: iterable over attribute names.
:parameter result: instance of obhject to estract attributes from.
:parameter appmodel: optional instance of :class:`djpcms.views.Application`.
'''
    if not appmodel:
        appmodel = djp.view.site.for_model(result.__class__)
    if not mapper and appmodel:
        mapper = appmodel.mapper
    if mapper:
        getr = get_app_result(mapper,actions)
    else:
        if hasattr(result,'__iter__'):
            getr = get_iterable_result(result)
        else:
            getr = get_result()
    return {'id': getr.id(result),
            'display': (getr(djp.request,name,result,appmodel,**kwargs)\
                        for name in headers)}


class get_result(object):
    __slots__ = ('first',)
    def __init__(self):
        self.first = True
        
    def id(self, result):
        return None

    def __call__(self, request, field_name, result, appmodel, **kwargs):
        return field_repr(field_name, result, appmodel = appmodel, **kwargs)
    
    
class get_iterable_result(object):
    
    def __init__(self, results):
        self.iter = iter(results)
        
    def id(self, result):
        return None

    def __call__(self, request, field_name, result, appmodel, **kwargs):
        try:
            return nicerepr(next(self.iter),**kwargs)
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
    
    def __call__(self, request, field_name, result, appmodel,
                 nd = 3, path = None, escape = None, **kwargs):
        mapper = self.mapper
        first = self.first
        url = None
        if field_name:
            result_repr = field_repr(field_name, result, appmodel = appmodel, nd = nd)
            if(self.first and not appmodel.list_display_links) or \
                    field_name in appmodel.list_display_links:
                first = False
                url = appmodel.viewurl(request, result, field_name = field_name)
            
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
        return var
    