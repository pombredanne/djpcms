from collections import namedtuple

from py2py3 import zip, to_string, itervalues

from djpcms import UnicodeMixin
from djpcms.utils import smart_escape
from djpcms.utils.text import nicename
from djpcms.template import loader

from .base import WidgetMaker, Widget
from .widgets import DefinitionList
from .apptools import application_views, application_links
from .nicerepr import results_for_item


__all__ = ['ObjectItem',
           'ObjectDef',
           'ObjectPagination']
            

class ObjectItem(WidgetMaker):
    tag = 'div'
    default_class='item-view'

    def addid(self, widget, context):
        id = context['appmodel'].mapper.unique_id(context['instance'])
        widget.addAttr('id',id)
         
    def definition_list(self, djp, context):
        appmodel = context['appmodel']
        headers = appmodel.object_display
        mapper = appmodel.mapper
        ctx = results_for_item(djp,
                               headers,
                               context['instance'],
                               appmodel,
                               escape = smart_escape)
        display = ctx.pop('display')
        items = ((head.name,value) for head,value in zip(headers,display))
        return DefinitionList(data_stream = items, cn = 'object-definition')\
                    .addClass(mapper.module_name)
         
    def get_context(self, djp, widget, keys):
        ctx = super(ObjectItem,self).get_context(djp, widget, keys)
        links = dict(((elem['view'].name,elem) for\
                       elem in application_views(ctx['appmodel'],
                                                 djp,
                                                 instance = ctx['instance'])))
        view = links.pop('view',None)
        if not view:
            view = links.pop('change',None)
        ctx['links'] = links
        ctx['view'] = view
        ctx['link_list'] = itervalues(links)
        return ctx
    
    def code_or_url(self, context):
        view = context.get('view',None)
        if view:
            item = list(application_links([view],asbuttons=False))[0][1]
        else:
            item = str(context['instance'])
        return item
    
    def stream(self, djp, widget, context):
        yield self.code_or_url(context)
    
    
class ObjectDef(ObjectItem):
    '''Simply display a definition list for the object.'''
    tag = None
        
    def stream(self, djp, widget, context):
        dl = self.definition_list(djp, context)
        self.addid(dl, context)
        yield dl.render(djp)

    
class ObjectPagination(ObjectItem):
    default_class = 'pagination-item'
    default_style = 'ui-widget ui-widget-content'

