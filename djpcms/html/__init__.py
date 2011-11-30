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
from .context import *
from .base import *
from .widgets import *
from .grid960 import *
from .htmltype import *
from .box import *
from .nicerepr import *
from .table import *
from .tabs import *
from .yui import *
from .template import *


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

