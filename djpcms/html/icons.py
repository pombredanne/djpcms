
__all__ = ['with_icon']


def with_icon(name=None, size=None, widget=None):
    if name:
        return _icon_handler(name, size, widget)
    else:
        return widget

def set_icon_handler(handler):
    global _icon_handler
    _icon_handler = handler
    
def _icon(name, size=None, widget=None):
    if widget:
        return widget
    else:
        return ''

_icon_handler = _icon
    