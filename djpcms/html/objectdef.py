from collections import namedtuple

from py2py3 import zip, to_string, itervalues

from djpcms import UnicodeMixin
from djpcms.utils import smart_escape
from djpcms.utils.text import nicename
from djpcms.template import loader

from .base import WidgetMaker, Widget
from .apptools import application_links
from .nicerepr import results_for_item


OBJECT_DEF_TEMPLATE = 'djpcms/object_definition.html'

__all__ = ['ObjectDefinition',
           'ObjectItem',
           'ObjectDef',
           'ObjectPagination']


#def add_definition(data, name, value):
#    data.append({'name':name,'value':value})

class ObjectDefinition(UnicodeMixin):
    '''Utility class for displaying an
object instance as html.

:parameter appmodel: instance of :class:`djpcms.views.ModelApplication`.
:parameter djp: instance of :class:`djpcms.views.DjpResponse`.
:parameter data: Optional data to display. If not provided, the data
                 is evaluated using the settings in ``appmodel``.
                 The format of this data is an iterable over dictionaries
                 containing `name` and `value` entries.

Usage::

    >>> d = ObjectDefinition(myapp, djp)
    >>> str(d)
    
'''
    def __init__(self, appmodel, djp, data = None, instance = None):
        self.appmodel = appmodel
        self.djp = djp
        self.data = data
        self.mapper = None if not appmodel else appmodel.mapper
        self.obj = instance if instance is not None else djp.instance
           
    def __unicode__(self):
        '''Render an object as definition list.'''
        appmodel = self.appmodel
        mapper = self.mapper
        if self.data:
            ctx = {'id':None if not mapper else mapper.unique_id(self.obj)}
            items = self.data
        else:
            headers = self.appmodel.object_display
            label_for_field = nicename if not mapper else mapper.label_for_field
            ctx = results_for_item(self.djp,
                                   headers,
                                   self.obj,
                                   self.appmodel,
                                   escape = smart_escape)
            display = ctx.pop('display')
            items = ({'name':label_for_field(name),'value':value}\
                        for name,value in zip(headers,display))
        ctx.update({'item':self.obj,
                    'items': items})
        if mapper:
            template = ('{0}/{1}_definition.html'.format(mapper.app_label,mapper.module_name),
                        OBJECT_DEF_TEMPLATE)
            ctx.update({'module_name':mapper.module_name})
        else:
            template = OBJECT_DEF_TEMPLATE
        return loader.render(template, ctx)
        

class ObjectItem(WidgetMaker):
    tag = 'div'
    default_class='list-item'

    def get_context(self, djp, widget, keys):
        ctx = super(ObjectItem,self).get_context(djp, widget, keys)
        links = dict(application_links(ctx['appmodel'],
                                       djp,
                                       instance = ctx['instance'],
                                       asbuttons = False,
                                       as_widget = True))
        view = links.pop('view',None)
        if not view:
            view = links.pop('change',None)
        ctx['links'] = links
        ctx['view'] = view
        ctx['link_list'] = itervalues(links)
        return ctx
        
    def stream(self, djp, widget, context):
        view = context.get('view',None)
        if view:
            item = view
        else:
            item = str(context['instance'])
        yield item


class ObjectDef(ObjectItem):
    tag = None
    
    def inner(self, djp, widget, keys):
        appmodel = widget.internal['appmodel']
        instance = widget.internal['instance']
        return to_string(ObjectDefinition(appmodel, djp,
                                          instance=instance))
            
            
class ObjectPagination(ObjectItem):
    default_class = 'pagination-item'
