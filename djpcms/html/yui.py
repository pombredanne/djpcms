
from .base import WidgetMaker, Widget

__all__ = ['yuigrid3']


class YuiGrid3(WidgetMaker):
    tag = 'div'
    default_class = 'yui3-g'
    
    def data2html(self, djp, data):
        val = super(YuiGrid3,self).data2html(djp,data[0])
        size = data[1]
        c1 = '<div class="yui3-u-{0}-{1}">'.format(*size)
        return c1 + val + '</div>'
    
    
_YuiGrid3 = YuiGrid3()
    
    
def yuigrid3(*chunks, **kwargs):
    '''Render a yui3_ grid with a given number of *chunks*.
    
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