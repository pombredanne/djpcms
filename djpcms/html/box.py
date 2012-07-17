from djpcms.media import Media

from .base import Widget, Div
from .icons import with_icon
from . import classes

__all__ = ['box', 'panel']


def panel(content):
    return Widget('div', content,
                  cn=(classes.panel, classes.widget_body, classes.corner_all))
    

class BoxTemplate(Div):
    classes = (classes.widget, classes.box)
    _media = Media(js = ['djpcms/collapse.js'])
    
    def media(self, request, widget):
        if widget.hasClass('collapsable'):
            return self._media
    

Box = BoxTemplate().add(
        Div(cn=(classes.widget_head, classes.corner_top, 'hd'), key='hd'),
        Div(cn=(classes.widget_body, 'bd'), key='bd'),
        Div(cn=(classes.widget_foot, classes.corner_bottom, 'ft'), key='ft'))

BoxNoFooter = BoxTemplate().add(
        Div(cn=(classes.widget_head, classes.corner_top, 'hd'), key='hd'),
        Div(cn=(classes.widget_body, classes.corner_bottom, 'bd'), key='bd'))


def box(hd='', bd='', ft=None, minimize=False, detachable=False,
        collapsable=False, collapsed=False, edit_menu=None,
        **kwargs):
    '''Create a box :class:`Widget`.'''
    if ft is not None:
        b = Box(**kwargs)
        b['ft'].add(ft)
    else:
        b = BoxNoFooter(**kwargs)
    b['bd'].add(bd)
    if not edit_menu:
        edit_menu = Widget('ul')
    if collapsed:
        b.addClass('collapsed')
        collapsable = True
        b['bd'].hide()
    if detachable:
        detach = with_icon('detach-box')
        attach = with_icon('attach-box')
        b.addData('icons',{'detach': detach, 'attach': attach})
        b.addClass('detachable')
        edit_menu.add(Widget('a', detach, href='#'))
    # If the box is collapsable add collapsable class to it
    if collapsable:
        open = with_icon('open-box')
        close = with_icon('close-box') 
        b.addData('icons',{'close': close, 'open': open})
        b.addClass('collapsable')
        icon = open if collapsed else close
        edit_menu.add(Widget('a', icon, cn='collapse', href='#'))
    header = b['hd']
    header.add(Widget('h3', hd))
    if edit_menu:
        header.add(edit_menu.addClass(classes.edit_menu))
    return b

