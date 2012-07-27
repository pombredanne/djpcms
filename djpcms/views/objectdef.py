from collections import namedtuple

from djpcms import html
from djpcms.html import WidgetMaker, Widget, classes
from djpcms.utils.httpurl import zip, to_string, itervalues
from djpcms.utils.text import UnicodeMixin, smart_escape

from .pagination import application_views, application_links


__all__ = ['ObjectItem',
           'ObjectDef',
           'ObjectPagination']


class ObjectItem(WidgetMaker):
    tag = 'div'
    classes = 'item-view'

    def stream(self, request, widget, context):
        instance = widget.internal.get('instance') or request.instance
        yield str(instance)


class ObjectDef(WidgetMaker):
    '''Simply display a definition list for the object.'''
    tag = 'div'
    classes = classes.object_definition

    def get_context(self, request, widget, context):
        appmodel = widget.internal.get('appmodel',request.view.appmodel)
        instance = widget.internal.get('instance',request.instance)
        if instance is None:
            return
        headers = appmodel.object_display
        mapper = appmodel.mapper
        ctx = html.results_for_item(request,
                                    headers,
                                    instance,
                                    appmodel)
        display = ctx.pop('display')
        items = (Widget('dl',(head.name,value))\
                                for head,value in zip(headers,display))
        widget.add(items)


class ObjectPagination(ObjectItem):
    default_class = 'pagination-item'
    default_style = 'ui-widget ui-widget-content'

