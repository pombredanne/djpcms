from collections import namedtuple

from djpcms import html
from djpcms.utils.py2py3 import UnicodeMixin, zip, to_string, itervalues 
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
         
    def get_context(self, request, widget, context):
        instance = widget.internal.get('instance') or request.instance
        context['instance']
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
    
    
class ObjectDef(html.DefinitionList):
    '''Simply display a definition list for the object.'''
    classes = 'object-definition'
    
    def get_context(self, request, widget, context):
        appmodel = widget.internal.get('appmodel',request.view.appmodel)
        instance = widget.internal.get('instance',request.instance)
        if instance is None:
            return
        headers = appmodel.object_display
        mapper = appmodel.mapper
        widget.addClass(mapper.module_name)
        ctx = html.results_for_item(request,
                                    headers,
                                    instance,
                                    appmodel)
        display = ctx.pop('display')
        items = ((head.name,value) for head,value in zip(headers,display))
        widget.add(items)

    
class ObjectPagination(ObjectItem):
    default_class = 'pagination-item'
    default_style = 'ui-widget ui-widget-content'

