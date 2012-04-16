'''Font icons from

http://fortawesome.github.com/Font-Awesome/
'''
from djpcms.html import Widget
from djpcms.html.icons import set_icon_handler

# ICONS NAME MAPPING
mapping = {'admin': 'cog',
           'edit': 'pencil',
           'delete': 'trash',
           'delete_all': 'trash',
           'add': 'plus',
           'true': 'ok',
           'false': 'minus-sign',
           'logout': 'signout',
           'login': 'signin'}


def icon(name, size, widget):
    name = mapping.get(name, name)
    inner = Widget('i', cn='icon-{0}'.format(name))
    if size:
        inner.addClass('icon-{0}'.format(size))
    if widget:
        widget.insert(0, inner)
        widget.insert(1, ' ')
        return widget
    else:
        return inner.render()

    
set_icon_handler(icon)
