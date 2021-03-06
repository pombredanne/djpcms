'''\
A collection of classes and Mixins for rendering HTML widgets.
Used throughout the library including the :mod:`djpcms.forms.layout`
module.

A simple usage::

    >>> from djpcms import html
    >>> text = html.Widget('input:text', name = 'plugin', value='Random', cn='plg')
    >>> text.flatatt()
    ' type="text" name="plugin" value="Random" class="plg"'
    >>> text.render()
    '<input type="text" name="plugin" value="Random" class="plg"/>'
    >>> text.addClass('foo').render()
    '<input type="text" name="plugin" value="Random" class="plg foo"/>'
'''
from .icons import *
from .base import *
from .widgets import *
from .nicerepr import *
from .box import *
from .table import *
from .tabs import *
from .doc import *
from .snippets import *


def block(stream, id = None, cn = None, djp = None):
    div = Widget('div', id = id, cn = 'djpcms-block').addClass(cn)
    return div.render(djp = djp, inner = '\n'.join(stream))


class blockelement(Widget):
    maker = 'div'
    wrap_class = 'djpcms-block-element'
    
    def __init__(self, b, **kwargs):
        self._b = b
        super(blockelement,self).__init__(**kwargs)
        self.addClass(self.wrap_class)

    def render(self, djp = None, inner = None):
        inner = self._b.render(djp)
        return super(blockelement,self).render(djp,inner)
    
def legend(text, cn='legend', **kwargs):
    return Widget('div', text, cn=cn, **kwargs)

def render_block(f):
    def _(self, request, block=None, **kwargs):
        content = f(self, request, block=block, **kwargs)
        if block is None and not request.is_xhr:
            content = panel(content)
        return content
    return _
