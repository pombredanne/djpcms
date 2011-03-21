from py2py3 import zip

from djpcms import UnicodeMixin
from djpcms.utils import smart_escape
from djpcms.template import loader

from .table import result_for_item


OBJECT_DEF_TEMPLATE = 'djpcms/object_definition.html'

__all__ = ['ObjectDefinition']


class ObjectDefinition(UnicodeMixin):
    '''Utility class for displaying an
object instance as html.

:parameter appmodel: instance of :class:`djpcms.views.ModelApplication`.
:parameter djp: instance of :class:`djpcms.views.DjpResponse`.

Usage::

    >>> d = ObjectDefinition(myapp, djp)
    >>> str(d)
    
'''    
    def __init__(self, appmodel, djp, data = None):
        self.appmodel = appmodel
        self.djp = djp
        self.obj = djp.instance
        self.data = data
        
    def _data(self):
        obj = self.obj
        mapper = self.appmodel.mapper
        label_for_field = mapper.label_for_field
        getrepr = mapper.getrepr
        mark_safe = loader.mark_safe
        for field in self.appmodel.object_display:
            name = label_for_field(field)
            yield {'name':name,
                   'value':smart_escape(getrepr(field,obj))}
                
    def __unicode__(self):
        '''Render an object as definition list.'''
        appmodel = self.appmodel
        mapper = appmodel.mapper
        headers = self.appmodel.object_display
        label_for_field = mapper.label_for_field
        if self.data:
            ctx = {'id':mapper.get_object_id(self.obj)}
            items = self.data
        else:
            ctx = result_for_item(self.djp,headers,
                                  self.obj,mapper,appmodel)
            display = ctx.pop('display')
            items = ({'name':label_for_field(name),'value':value}\
                        for name,value in zip(headers,display))
        ctx.update({'module_name':mapper.module_name,
                    'item':self.obj,
                    'items': items})
        return loader.render(('%s/%s_definition.html' % (mapper.app_label,mapper.module_name),
                              OBJECT_DEF_TEMPLATE),
                              ctx)
        