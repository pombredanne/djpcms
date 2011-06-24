'''\
A collection of classes and Mixins for rendering HTML widgets.
Used throughout the library including the :mod:`djpcms.forms`
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
from .utils import *
from .media import *
from .base import *
from .widgets import *
from .pagination import *
from .grid960 import *
from .htmltype import *
from .box import *
from .nicerepr import *
from .objectdef import *
from .apptools import *
from .table import *

