from decimal import Decimal

from .pycss import mixin, css, as_mixin, deval

__all__=  ['clearfix', 'shadow', 'gradient',
           'grid', 'fluidgrid']

################################################# CLEARFIX
class clearfix(mixin):
    '''For clearing floats to all *elements*.'''
    def __init__(self, elements):
        self.mixin = as_mixin(elements)
    
    def __call__(self):
        for elem in self.mixin.css():
            tag = elem.tag
            elem['*zoom'] = 1
            yield elem
            yield css(tag+':before,'+tag+':after',
                      display = 'table',
                      content = '""')
            yield css(tag+':after', clear = 'both')
            
            
################################################# CSS3
class shadow(mixin):
    def __init__(self, elements, shadow):
        self.mixin = as_mixin(elements)
        self.shadow = shadow
        
    def __call__(self):
        for elem in self.mixin.css():
            elem['-webkit-box-shadow'] = self.shadow
            elem['   -moz-box-shadow'] = self.shadow
            elem['        box-shadow'] = self.shadow
            yield elem
        
        
class radius(mixin):
    def __init__(self, elements, radius):
        self.mixin = as_mixin(elements)
        self.radius = radius
        
    def __call__(self):
        for elem in self.mixin.css():
            elem['-webkit-border-radius'] = self.radius
            elem['   -moz-border-radius'] = self.radius
            elem['        border-radius'] = self.radius
            yield elem


class gradient(mixin):
    def __init__(self, elements, direction_start_end):
        self.mixin = as_mixin(elements)
        self.direction_start_end = direction_start_end
        
    def __call__(self):
        d,s,e = deval(self.direction_start_end)
        if d in ('h','v','r','s'):
            self.decorate = getattr(self, d+'gradient')
        else:
            d = int(d)
            self.decorate = self.dgradient
        for elem in self.mixin.css():
            yield self.decorate(elem,d,s,e)
            
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
        return elem
        
    def hgradient(self, elem, d, s, e):
        return self._gradient(elem, 'left', s, e)
        
    def vgradient(self, elem, d, s, e):
        return self._gradient(elem, 'top', s, e)

        
################################################# FIXED GRID MIXIN
class grid(mixin):
    grid_class = ''
    unit = 'px'
    def __init__(self, columns, span = 40, gutter = 20):
        if columns <=1:
            raise ValueError('Grid must have at least 2 columns')
        self.span = span
        self.gutter = gutter
        self.columns = columns
        self.width = columns*span + (columns-1)*gutter
    
    def row(self, tag):
        m = '{0}{1}'.format(self.gutter,self.unit)
        return css(tag, margin_left = m)
    
    def container(self, tag):
        return css(tag, width = '{0}px'.format(self.width),
                   margin_left = 'auto',
                   margin_right = 'auto')
        
    def __call__(self):
        row = '.{0}_{1}'.format('row'+self.grid_class,self.columns)
        yield clearfix(self.row(row))
        for s in range(1,self.columns+1):
            w = '{0}{1}'.format(s*self.span + (s-1)*self.gutter,self.unit)
            yield css('{0} > .span{1}'.format(row,s), width=w)
        yield css('{0} > [class*="span"]'.format(row),
                  float='left',
                  margin_left='{0}{1}'.format(self.gutter,self.unit))
        yield clearfix(self.container('.grid-container'+self.grid_class))
        

################################################# FLUID GRID MIXIN        
class fluidgrid(grid):
    grid_class = '-fluid'
    unit = '%'
    def __init__(self, columns, gutter = 2.5641):
        if columns <=1:
            raise ValueError('Grid must have at least 2 columns')
        if gutter < 0:
            raise ValueError('gutter must be positive')
        self.columns = columns
        self.gutter = gutter
        self.span = round((100 - (columns-1)*gutter)/columns,4)
        if self.span <= 0:
            raise ValueError('gutter too large')
    
    def row(self, tag):
        return css(tag, width = '100%')
    
    def container(self, tag):
        return css(tag, padding_left = '20px', padding_right = '20px')