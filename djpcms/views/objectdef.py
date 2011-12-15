from collections import namedtuple

from py2py3 import zip, to_string, itervalues

from djpcms import UnicodeMixin, html
from djpcms.utils import smart_escape

from .pagination import application_views, application_links


__all__ = ['ObjectItem',
           'ObjectDef',
           'ObjectPagination']
    

class ObjectItem(html.WidgetMaker):
    tag = 'div'
    default_class='item-view'
         
    def definition_list(self, request, context):
        appmodel = context['appmodel']
        headers = appmodel.object_display
        mapper = appmodel.mapper
        ctx = html.results_for_item(request,
                                    headers,
                                    context['instance'],
                                    appmodel,
                                    escape = smart_escape)
        display = ctx.pop('display')
        items = ((head.name,value) for head,value in zip(headers,display))
        return html.DefinitionList(data_stream = items, cn = 'object-definition')\
                    .addClass(mapper.module_name)
         
    def get_context(self, request, widget, keys):
        ctx = super(ObjectItem,self).get_context(request, widget, keys)
        instance = ctx['instance']
        ctx['links'] = list(application_views(request, instance = instance))
        return ctx
    
    def code_or_url(self, context):
        view = context.get('view',None)
        if view:
            item = list(application_links([view],asbuttons=False))[0][1]
        else:
            item = str(context['instance'])
        return item
    
    def stream(self, request, widget, context):
        yield self.code_or_url(context)
    
    
class ObjectDef(ObjectItem):
    '''Simply display a definition list for the object.'''
    tag = None
        
    def stream(self, request, widget, context):
        dl = self.definition_list(request, context)
        yield dl.render(request)

    
class ObjectPagination(ObjectItem):
    default_class = 'pagination-item'
    default_style = 'ui-widget ui-widget-content'

