from datetime import date
from inspect import isclass
import logging

from djpcms.utils import orms
from djpcms.utils.httpurl import zip
from djpcms.utils.dates import smart_time
from djpcms.utils.numbers import significant_format
from djpcms.utils.text import to_string, mark_safe, escape, nicename, is_safe

from .base import Widget
from .icons import with_icon
from . import classes


__all__ = ['nicerepr',
           'field_repr',
           'results_for_item',
           'action_checkbox',
           'object_definition',
           'NONE_VALUE']


NONE_VALUE = '(None)'
NONE_VALUE = float('nan')
#divchk = '<div class="action-check">{0}<span class="value">{1}</span></div>'
divchk = '<div class="action-check">{0}{1}</div>'

logger = logging.getLogger('djpcms.nicerepr')


def action_checkbox(val, id):
    '''Return html for the action checkbox'''
    if val:
        chk = Widget('input:checkbox', name = 'action-item', value = id)
        val = divchk.format(chk.render(),val)
    return mark_safe(val)


def nicerepr(val, nd=None, none_value=NONE_VALUE, dateformat=None,
             timeformat=None, settings=None, **kwargs):
    '''Prettify a value to be displayed in html.

:parameter val: value to prettify.
:parameter nd: numerical accuracy for floating point numbers.
'''
    if val is None:
        return NONE_VALUE
    elif is_safe(val):
        return val
    elif isinstance(val, date):
        return smart_time(val,dateformat,timeformat,settings)
    elif isinstance(val, bool):
        if val:
            return with_icon('true')
        else:
            return with_icon('false')
    else:
        val = to_string(val)
        try:
            return significant_format(val, n=nd)
        except ValueError:
            if val.startswith('http://') or val.startswith('https://'):
                val = mark_safe('<a href="{0}">{0}</a>'.format(val))
            return val

def field_repr(request, head, obj, appmodel):
    '''Retrive the value of field specified in *head* from an object *obj*.'''
    val = None
    attrname = head.attrname
    if hasattr(obj, attrname):
        try:
            val = getattr(obj, attrname)
            if not isclass(val) and hasattr(val, '__call__'):
                val = val()
        except Exception as e:
            val = str(e)
            logger.error('Unhadled exception in field representation',
                         exc_info=True)
    elif hasattr(obj, '__getitem__') and field_name in obj:
        val = obj[field_name]
    if appmodel:
        obj = orms.orm_instance(obj)
        val = appmodel.instance_field_value(request, obj, head.code, val)
    return nicerepr(val, settings=request.settings)


def results_for_item(request, headers, result, appmodel=None, actions=None,
                     **kwargs):
    '''Return an iterable over values in result given by attributes in headers.

:parameter headers: iterable over attribute names.
:parameter result: instance of obhject to estract attributes from.
:parameter appmodel: optional instance of :class:`djpcms.views.Application`.
'''
    if appmodel and appmodel.mapper:
        result = appmodel.mapper.instance(result)
        getr = get_app_result(appmodel.mapper, actions)
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
        return field_repr(request, head, result, appmodel)


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

    def __init__(self, mapper, actions=False):
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
        link = None
        if(first and not appmodel.list_display_links) or \
           head.code in appmodel.list_display_links:
            if first:
                name = 'view'
                first = False
            else:
                name = None
            link = appmodel.instance_field_view(request,
                                                result,
                                                field_name=head.code,
                                                asbutton=False,
                                                icon=False,
                                                name=name)
        if link:
            var = link.render()
        else:
            var = field_repr(request, head, result, appmodel)
        if self.first and self.actions and mapper:
            first = False
            var = action_checkbox(var, mapper.id(result))
        esc = kwargs.get('escape', escape)
        var = esc(var)
        self.first = first
        return var


def object_definition(request, instance=None, appmodel=None, block=None):
    appmodel = appmodel or request.view.appmodel
    instance = instance or request.instance
    if not appmodel or not instance:
        return ''
    headers = appmodel.object_fields(request)
    mapper = appmodel.mapper
    widget = Widget('div', cn=classes.object_definition)\
                    .addClass(mapper.htmlclass)
    ctx = results_for_item(request, headers, instance, appmodel)
    display = ctx.pop('display')
    items = (Widget('dl',(head.name,value))\
                            for head,value in zip(headers, display))
    return widget.add(items)