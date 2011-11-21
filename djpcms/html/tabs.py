from djpcms.utils import gen_unique_id

from .base import Widget, WidgetMaker, iterable

__all__ = ['TabsMaker','tabs']


class TabsMaker(WidgetMaker):
    tag = 'div'
    default_class = 'ui-tabs'
    
    def add_to_widget(self, widget, keyvalue, value = None):
        if value is None and iterable(keyvalue):
            key, value = tuple(keyvalue)
        else:
            key, value = keyvalue, value
        widget.data_stream.append((key, value))
        
    def stream(self, djp, widget, context):
        if widget.data_stream:
            ul = Widget('ul')
            di = []
            for key,val in widget.data_stream:
                id = gen_unique_id()[:8]
                ul.add(Widget('a',key,href='#{0}'.format(id)))
                di.append(Widget('div',val,id=id).render(djp))
            yield ul.render(djp)
            yield '\n'.join(di)
        
    
_maker = TabsMaker()

def tabs(data_stream = None, **kwargs):
    kwargs['maker'] = _maker
    return Widget(data_stream = data_stream, **kwargs)