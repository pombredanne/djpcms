
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
    return Widget(_YuiGrid3, data_stream = chunks, **kwargs)