from djpcms.utils import gen_unique_id

from .base import Widget, WidgetMaker
from .widgets import List

__all__ = ['TabsMaker','tabs']


class TabsMaker(WidgetMaker):
    tag = 'div'
    default_class = 'ui-tabs'
    
    def stream(self, djp, widget, context):
        if widget.data_stream:
            ul = List()
            di = []
            for key,value in widget.data_stream:
                id = gen_unique_id()[:8]
                ul.addanchor('#{0}'.format(id),key)
                di.append(Widget('div',id=id).render(inner = value))
            yield ul.render()
            yield '\n'.join(di)
    
    
class tabs(Widget):
    maker = TabsMaker()