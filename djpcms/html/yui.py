
from .base import WidgetMaker, Widget

__all__ = ['yuigrid3','yuigrid3stream']


class YuiGrid3(WidgetMaker):
    tag = 'div'
    default_class = 'yui3-g'
    
    def data2html(self, request, data):
        val = super(YuiGrid3,self).data2html(request,data[0])
        size = data[1]
        c1 = '<div class="yui3-u-{0}-{1}">'.format(*size)
        return c1 + val + '</div>'
    
    
_YuiGrid3 = YuiGrid3()
    
    
def yuigrid3(*chunks, **kwargs):
    '''Return a :class:`Widget` instance which render a yui3_ grid
with a given number of *chunks*.
    
:parameter chunks: positional arguments made of 2-elements tuples of
    the form::
    
        (txt1,size1),(txt2,size2),...

    where ``txt`` is either a string or an instance of a :class:`Widget` and
    ``size`` is the 2-elements tuple defining the size of the block.
    For example::
    
        ("Fills 1/3 of available width",(1,3)),
        ("Fills 2/3 of available width",(2,3))
        
    are valid inputs.
    
.. _yui3: http://yuilibrary.com/yui/docs/cssgrids/
'''
    return Widget(_YuiGrid3, data_stream = chunks, **kwargs)


class yuigrid3stream(object):
    
    def __init__(self, *sizes):
        self.sizes = sizes
        self.pos = 0
        
    def __call__(self, djp, data):
        if isinstance(data,Widget):
            data = data.render(djp)
        if self.pos >= len(self.sizes):
            self.pos = 0
        r = _YuiGrid3.data2html(djp,(data,self.sizes[self.pos]))
        self.pos += 1
        return r
    