from decimal import Decimal

from .pycss import mixin, css, cssa, deval

__all__=  ['clearfix', 'fixtop', 'shadow', 'radius', 'gradient']

################################################# CLEARFIX
class clearfix(mixin):
    '''For clearing floats to all *elements*.'''    
    def __call__(self, elem):
        elem['*zoom'] = 1
        yield cssa('before,after',
                   parent = elem,
                   display = 'table',
                   content = '""')
        yield cssa('after',
                   parent = elem,
                   clear = 'both')
            
################################################# FIXTOP
class fixtop(mixin):
    '''For clearing floats to all *elements*.'''
    def __init__(self, zindex = 2000):
        self.zindex = zindex
            
    def __call__(self, elem):
        elem['left'] = 0
        elem['top'] = 0
        elem['right'] = 0
        elem['position'] = 'fixed'
        elem['zindex'] = self.zindex
        
            
################################################# CSS3
class shadow(mixin):
    def __init__(self, shadow):
        self.shadow = shadow
        
    def __call__(self, elem):
        elem['-webkit-box-shadow'] = self.shadow
        elem['   -moz-box-shadow'] = self.shadow
        elem['        box-shadow'] = self.shadow
        
        
class radius(mixin):
    def __init__(self, radius):
        self.radius = radius
        
    def __call__(self, elem):
        r = self.radius
        if hasattr(r,'__call__'):
            r = r()
        elem['-webkit-border-radius'] = r
        elem['   -moz-border-radius'] = r
        elem['        border-radius'] = r


class gradient(mixin):
    def __init__(self, direction_start_end):
        self.direction_start_end = direction_start_end
        
    def __call__(self, elem):
        d,s,e = deval(self.direction_start_end)
        if d in ('h','v','r','s'):
            self.decorate = getattr(self, d+'gradient')
        else:
            d = int(d)
            self.decorate = self.dgradient
        self.decorate(elem,d,s,e)
            
    def _gradient(self, elem, l, s, e):
        p = '100% 0' if l == 'left' else '0 100%'
        t = 1 if l == 'left' else 0
        #
        elem['background-color'] = e;
        elem['background-image'] =\
        '-moz-linear-gradient({2}, {0}, {1})'.format(s,e,l)
        #
        elem['background-image'] =\
        '-ms-linear-gradient({2}, {0}, {1})'.format(s,e,l)
        #
        # Safari 4+, Chrome 2+
        elem['background-image'] =\
        '-webkit-gradient(linear, 0 0, {2}, from({0}), to({1}))'.format(s,e,p)
        #
        # Safari 5.1+, Chrome 10+
        elem['background-image'] =\
        '-webkit-linear-gradient({2}, {0}, {1})'.format(s,e,l)
        #
        # Opera 11.10
        elem['background-image'] =\
        '-o-linear-gradient({2}, {0}, {1})'.format(s,e,l)
        #
        # Le standard
        elem['background-image'] =\
        'linear-gradient({2}, {0}, {1})'.format(s,e,l)
        elem['background-repeat'] = 'repeat-x'
        # IE9 and down
        elem['filter'] = "progid:DXImageTransform.Microsoft.gradient(\
startColorstr='{0}', endColorstr='{1}', GradientType={2})".format(s,e,t)
        
    def hgradient(self, elem, d, s, e):
        self._gradient(elem, 'left', s, e)
        
    def vgradient(self, elem, d, s, e):
        self._gradient(elem, 'top', s, e)

        