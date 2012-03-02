from decimal import Decimal

from .pycss import mixin, css, as_mixin

__all__=  ['grid', 'fluidgrid']


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
        

################################################# FIXED GRID MIXIN
class grid(mixin):
    row_class = 'row'
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
        
    def __call__(self):
        row = '.{0}_{1}'.format(self.row_class,self.columns)
        yield clearfix(self.row(row))
        for s in range(1,self.columns+1):
            w = '{0}{1}'.format(s*self.span + (s-1)*self.gutter,self.unit)
            yield css ('{0} > .span{1}'.format(row,s), width=w)
        yield css('{0} > [class*="span"]'.format(row),
                  float='left',
                  margin_left='{0}{1}'.format(self.gutter,self.unit))
        

################################################# FLUID GRID MIXIN        
class fluidgrid(grid):
    row_class = 'row-fluid'
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