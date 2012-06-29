from djpcms.utils.text import gen_unique_id
from djpcms.media import Media

from .base import Widget, WidgetMaker, iterable_for_widget
from . import classes

__all__ = ['tabs','accordion','ajax_html_select']


class TabWidget(Widget):
    
    def addtab(self, key, value):
        '''Override to allow for tuples and single values.'''
        return self.add(((key,value),))
        
    @property
    def data_stream(self):
        return tuple(self._unwind())
    
    def _unwind(self):
        if self._data_stream:
            ul = Widget('ul').addClass(self.internal.get('type'))
            divs = []
            for key, val in self._data_stream:
                if not isinstance(key,Widget) or key.tag!='a':
                    id = gen_unique_id()[:8]
                    key = Widget('a', key, href='#'+id)
                    divs.append(Widget('div', val, id=id))
                ul.add(key)
            yield ul
            for div in divs:
                yield div        


class Accordion(TabWidget):
    
    def _unwind(self):
        for key, val in self._data_stream:
            yield Widget('div', Widget('h3', key), cn=classes.clickable)
            yield Widget('div', val, cn=classes.widget_body)
        

tab_media = Media(js = ['djpcms/tabs.js'])

tabs = WidgetMaker(tag='div',
                   widget=TabWidget,
                   cn='ui-tabs djph',
                   internal={'type':'tabs'},
                   media=tab_media)
pills = WidgetMaker(tag='div',
                    widget=TabWidget,
                    cn='ui-tabs djph',
                    internal={'type':'pills'},
                    media=tab_media)
accordion = WidgetMaker(tag='div',
                        widget=Accordion,
                        cn='ui-accordion-container djph')


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
