'''\
A collection of classes and Mixins for rendering HTML widgets.
Used throughout the library including the :mod:`djpcms.forms`
module.

A simple usage::

    >>> from djpcms import html
    >>> text = html.TextInput(name = 'plugin', value='Random', cn='plg')
    >>> text.flatatt()
    ' type="text" name="plugin" value="Random" class="plg"'
    >>> text.render()
    '<input type="text" name="plugin" value="Random" class="plg"/>'
    >>> text.addClass('foo').render()
    '<input type="text" name="plugin" value="Random" class="plg foo"/>'
'''
from py2py3 import to_string

from .utils import *
from .base import *
from .media import *
from .pagination import *
from .grid960 import *
from .htmltype import *
from .box import *
from .nicerepr import *
from .objectdef import *
from .widgets import *
from .table import *


class HtmlWrap(HtmlWidget):
    
    def __init__(self, *args, **kwargs):
        self._inner = kwargs.pop('inner','')
        super(HtmlWrap,self).__init__(*args, **kwargs)
        
    def inner(self, *args, **kwargs):
        if hasattr(self._inner,'render'):
            return self._inner.render(*args, **kwargs)
        else:
            return to_string(self._inner)
