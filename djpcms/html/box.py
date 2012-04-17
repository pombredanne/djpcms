from djpcms.utils.media import Media
from .base import Widget, WidgetMaker
from .icons import with_icon

__all__ = ['box']


class BoxTemplate(WidgetMaker):
    tag = 'div'
    classes = 'widget'
    _media = Media(js = ['djpcms/collapse.js'])
    
    def media(self, request, widget):
        if widget.hasClass('collapsable'):
            return self._media
    

BoxHeader = WidgetMaker(tag='div', cn='hd', key='hd')

Box = BoxTemplate().add(BoxHeader,
                        WidgetMaker(tag='div', cn='bd', key='bd'),
                        WidgetMaker(tag='div', cn='ft', key='ft'))

BoxNoFooter = BoxTemplate().add(BoxHeader,
                                WidgetMaker(tag='div', cn='bd', key='bd'))


def box(hd='', bd='', ft=None, minimize=False,
        collapsable=False, collapsed=False, edit_menu=None,
        **kwargs):
    '''Create a box :class:`Widget`.'''
    if ft:
        b = Box(**kwargs)
        b['ft'].add(ft)
    else:
        b = BoxNoFooter(**kwargs)
    b['bd'].add(bd)
    if collapsed:
        b.addClass('collapsed')
        collapsable = True
    # If the box is collapsable add collapsable class to it
    if collapsable:
        open = with_icon('open-box')
        close = with_icon('close-box') 
        b.addData('icons',{'close': close, 'open': open})
        b.addClass('collapsable')
        icon = open if collapsed else close
        if not edit_menu:
            edit_menu = Widget('ul')
        edit_menu.add(Widget('a', icon, cn='collapse', href='#'))
    header = b['hd']
    header.add(Widget('h2', hd))
    if edit_menu:
        header.add(edit_menu.addClass('edit-menu'))
    return b

