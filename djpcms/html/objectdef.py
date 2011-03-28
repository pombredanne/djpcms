from py2py3 import zip

from djpcms import UnicodeMixin
from djpcms.utils import smart_escape
from djpcms.utils.text import nicename
from djpcms.template import loader

from .nicerepr import results_for_item


OBJECT_DEF_TEMPLATE = 'djpcms/object_definition.html'

__all__ = ['ObjectDefinition']


#def add_definition(data, name, value):
#    data.append({'name':name,'value':value})

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
           
    def __unicode__(self):
        '''Render an object as definition list.'''
        appmodel = self.appmodel
        mapper = appmodel.mapper
        headers = self.appmodel.object_display
        if self.data:
            ctx = {'id':mapper.get_object_id(self.obj)}
            items = self.data
        else:
            label_for_field = nicename if not mapper else mapper.label_for_field
            ctx = results_for_item(self.djp,headers,
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
        