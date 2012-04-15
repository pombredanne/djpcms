# ICONS NAME MAPPING
from djpcms.html import Widget
from djpcms.html.icons import set_icon_handler


mapping = {'edit': 'pencil',
           'delete': 'trash',
           'delete_all': 'warning-sign',
           'add': 'plus-sign'}


def icon(name, size, widget):
    name = mapping.get(name, name)
    inner = Widget('i', cn='icon-{0}'.format(name))
    if size:
        inner.addClass('icon-{0}'.format(size))
    if widget:
        widget.insert(0, inner)
    else:
        widget = inner
    return widget

    
set_icon_handler(icon)
