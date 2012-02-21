from djpcms.utils import gen_unique_id

from .base import Widget, WidgetMaker, iterable_for_widget

__all__ = ['TabsMaker','tabs','Accordion','ajax_html_select']


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
        
    def stream(self, request, widget, context):
        if widget.data_stream:
            ul = Widget('ul')
            divs = []
            for key,val in widget.data_stream:
                id = gen_unique_id()[:8]
                ul.add(Widget('a',key,href='#{0}'.format(id)))
                divs.append(Widget('div', val, id=id))
            yield ul.render(request)
            for div in divs:
                yield div.render(request)
        

class Accordion(TabsMaker):
    tag = 'div'
    default_class = 'ui-accordion-container djph'
    
    def stream(self, request, widget, context):
        if widget.data_stream:
            ul = Widget('ul')
            di = []
            for key,val in widget.data_stream:
                yield Widget('h3',key).render(request)
                yield Widget('div',val).render(request)
        
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


def ajax_html_select(name_title_html, **kwargs):
    '''If no htmlid is provided, a new widget containing the target html
    is created and data is an iterable over three elements tuples.'''
    htmlid = gen_unique_id()[:8]
    target = Widget('div',id=htmlid)
    select = Widget('select', cn = 'text-select')\
                    .addData('target','#{0}'.format(htmlid))
    
    for name,title,body in name_title_html:
        select.add((name,title))
        target.add(Widget('div', body, cn = '{0} target'.format(name)))
                    
    return Widget(None,(select,target))
