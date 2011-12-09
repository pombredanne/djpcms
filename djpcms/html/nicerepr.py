from datetime import date, datetime
from inspect import isclass

from djpcms.utils.text import nicename
from djpcms.utils.dates import smart_time
from djpcms.utils.const import EMPTY_VALUE, EMPTY_TUPLE, NOTHING
from djpcms.utils import force_str, mark_safe, significant_format, escape

from .icons import yes,no
from .base import Widget


__all__ = ['nicerepr',
           'field_repr',
           'results_for_item',
           'action_checkbox',
           'NONE_VALUE']

FIELD_SPLITTER = '__'
NONE_VALUE = '(None)'
NONE_VALUE = float('nan')
divchk = '<div class="action-check">{0}<span class="value">{1}</span></div>'


def action_checkbox(val, id):
    '''Return html for the action checkbox'''
    if val:
        chk = Widget('input:checkbox', name = 'action-item', value = id)
        val = divchk.format(chk.render(),val)
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
            return significant_format(val, n = nd, thousand_sep = None)
        except TypeError:
            val = force_str(val)
            if val.startswith('http://') or val.startswith('https://'):
                val = mark_safe('<a href="{0}">{0}</a>'.format(val))
            return val
    
    
def field_repr(request, field_name, obj, appmodel = None, **kwargs):
    '''Retrive the value of attribute *field_name*
from an object *obj* by trying out
several possibilities in the following order.

* If *field_name* is not defined or empty it returns ``None``.
* If *field_name* is an attribute of *obj* it returns the value.
* If *obj* is a dictionary type object and *field_value* is in *obj*
     it returns the vaue.
* If *appmodel* is defined it invokes the
  :meth:`djpcms.views.Application.object_field_value`
* Return ``None``
'''
    val = None
    if hasattr(obj,field_name):
        try:
            val = getattr(obj,field_name)
            if not isclass(val) and hasattr(val,'__call__'):
                val = val()
        except Exception as e:
            val = str(e)
    elif hasattr(obj,'__getitem__') and field_name in obj:
        val = obj[field_name]
    
    if appmodel:
        val = appmodel.object_field_value(request, obj, field_name, val)

    return nicerepr(val,**kwargs)
            
            
def results_for_item(request, headers, result, appmodel = None, 
                     actions = None, **kwargs):
    '''Return an iterable over values in result given by attributes in headers.
    
:parameter headers: iterable over attribute names.
:parameter result: instance of obhject to estract attributes from.
:parameter appmodel: optional instance of :class:`djpcms.views.Application`.
'''
    if appmodel and appmodel.mapper:
        getr = get_app_result(appmodel.mapper,actions)
        id = getr.id(result)
    else:
        id = None
        if hasattr(result,'__iter__'):
            getr = get_iterable_result(result)
        else:
            getr = get_result()
    return {'id': id,
            'display': (getr(request,head,result,appmodel,**kwargs)\
                        for head in headers)}


class get_result(object):
    __slots__ = ('first',)
    def __init__(self):
        self.first = True

    def __call__(self, request, head, result, appmodel, **kwargs):
        return field_repr(request, head.attrname, result, appmodel = appmodel,
                          **kwargs)
    
    
class get_iterable_result(object):
    
    def __init__(self, results):
        self.iter = iter(results)

    def __call__(self, request, head, result, appmodel, **kwargs):
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
    
    def __call__(self, request, head, result, appmodel, **kwargs):
        mapper = self.mapper
        first = self.first
        url = None
        attrname = head.code if hasattr(result,head.code) else head.attrname
        result_repr = field_repr(request, attrname, result,
                                 appmodel = appmodel, **kwargs)
        if(self.first and not appmodel.list_display_links) or \
                head.code in appmodel.list_display_links:
            first = False
            url = appmodel.viewurl(request, result, field_name = head.code)
        
        var = result_repr
        if url:
            var = escape(var)
            if url != request.path:
                if head.function != head.code:
                    title = field_repr(request, head.function, result,
                                       appmodel = appmodel, **kwargs)
                else:
                    title = '{0} - {1}'.format(head.name,result_repr)
                var = mark_safe('<a href="{0}" title="{2}">{1}</a>'\
                                .format(url, var, title))
            else:
                var = mark_safe('<a>{0}</a>'.format(var))
        
        if self.first and self.actions:
            first = False 
            var = action_checkbox(var, getattr(result,'id',None))
        
        esc = kwargs.get('escape',escape)
        var = esc(var)
        self.first = first
        return var
    