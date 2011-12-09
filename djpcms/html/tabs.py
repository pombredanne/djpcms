from djpcms.utils import gen_unique_id

from .base import Widget, WidgetMaker, iterable_for_widget

__all__ = ['TabsMaker','tabs','accordion']


class TabsMaker(WidgetMaker):
    tag = 'div'
    default_class = 'ui-tabs'
    
    def add_to_widget(self, widget, keyvalue, value = None):
        '''Override to allow for tuples and single values.'''
        if value is None and iterable_for_widget(keyvalue):
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
        

class Accordion(TabsMaker):
    tag = 'div'
    default_class = 'ui-accordion-container djph'
    
    def stream(self, djp, widget, context):
        if widget.data_stream:
            ul = Widget('ul')
            di = []
            for key,val in widget.data_stream:
                yield Widget('h3',key).render(djp)
                yield Widget('div',val).render(djp)
        
_tabs_maker = TabsMaker()
_acc_maker = Accordion()



def tabs(data_stream = None, **kwargs):
    '''Create dynamic tabs or pills. The only input required is an iterable
over two elements tuple containing the title and the data to display for
each tab.'''
    kwargs['maker'] = _tabs_maker
    return Widget(data_stream = data_stream, **kwargs)

def accordion(data_stream = None, **kwargs):
    kwargs['maker'] = _acc_maker
    return Widget(data_stream = data_stream, **kwargs)