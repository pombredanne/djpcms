from decimal import Decimal

from .pycss import generator, css, deval
from .mixins import clearfix

__all__=  ['grid', 'fluidgrid']

        
################################################# FIXED GRID MIXIN
class grid(generator):
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
        return css(tag,
                   clearfix(),
                   margin_left = m)
    
    def container(self, tag):
        return css(tag,
                   clearfix(),
                   width = '{0}px'.format(self.width),
                   margin_left = 'auto',
                   margin_right = 'auto')
        
    def __call__(self):
        row = '.{0}_{1}'.format('row'+self.grid_class,self.columns)
        yield self.row(row)
        for s in range(1,self.columns+1):
            w = '{0}{1}'.format(s*self.span + (s-1)*self.gutter,self.unit)
            yield css('{0} > .span{1}'.format(row,s), width=w)
        yield css('{0} > [class*="span"]'.format(row),
                  float='left',
                  margin_left='{0}{1}'.format(self.gutter,self.unit))
        yield self.container('.grid-container'+self.grid_class)
        

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
        return css(tag,
                   clearfix(),
                   width = '100%')
    
    def container(self, tag):
        return css(tag,
                   clearfix(),
                   padding_left = '20px',
                   padding_right = '20px')
