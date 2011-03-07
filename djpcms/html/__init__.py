from py2py3 import to_string

from .pagination import *
from .grid960 import *
from .htmltype import *
from .box import *


class HtmlWrap(HtmlWidget):
    
    def __init__(self, *args, **kwargs):
        self._inner = kwargs.pop('inner','')
        super(HtmlWrap,self).__init__(*args, **kwargs)
        
    def inner(self, *args, **kwargs):
        if hasattr(self._inner,'render'):
            self._inner.render(*args, **kwargs)
        else:
            to_string(self._inner)
