'''Useful mixins and generators'''
from .base import *
from .colorvar import *

__all__ = ['include_css',
           'opacity',
           'clearfix',
           'fixtop',
           'shadow',
           'radius',
           'gradient',
           'bcd',
           'clickable',
           'horizontal_navigation',
           'grid',
           'fluidgrid']
 
    
################################################################################
##    BATTERY INCLUDED MIXINS
################################################################################


################################################# OPACITY
class opacity(mixin):
    def __init__(self, o):
        self.o = o
        
    def __call__(self, elem):
        elem['opacity'] = self.o
        elem['filter'] = 'alpha(opacity={0})'.format(100*self.o)
        
        
################################################# CLEARFIX
class clearfix(mixin):
    '''For clearing floats to all *elements*.'''    
    def __call__(self, elem):
        elem['*zoom'] = 1
        yield cssa(':before,:after',
                   parent = elem,
                   display = 'table',
                   content = '""')
        yield cssa(':after',
                   parent = elem,
                   clear = 'both')
            
################################################# FIXTOP
class fixtop(mixin):
    '''Fix an element at the top of the page.'''
    def __init__(self, zindex = 2000):
        self.zindex = self.cleanup(zindex,'zindex')
            
    def __call__(self, elem):
        elem['left'] = 0
        elem['top'] = 0
        elem['right'] = 0
        elem['position'] = 'fixed'
        elem['z_index'] = Variable.cssvalue(self.zindex)
        
            
################################################# CSS3 BOX SHADOW
class shadow(mixin):
    def __init__(self, shadow):
        self.shadow = self.cleanup(shadow,'shadow')
        
    def __call__(self, elem):
        shadow = Variable.cssvalue(self.shadow)
        if shadow is not None:
            elem['-webkit-box-shadow'] = shadow
            elem['   -moz-box-shadow'] = shadow
            elem['        box-shadow'] = shadow
        
################################################# CSS3 RADIUS        
class radius(mixin):
    def __init__(self, radius):
        self.radius = self.cleanup(radius,'radius')
        
    def __call__(self, elem):
        r = Variable.cssvalue(self.radius)
        if r is not None:
            elem['-webkit-border-radius'] = r
            elem['   -moz-border-radius'] = r
            elem['        border-radius'] = r
g_radius = radius

################################################# CSS3 GRADIENT
class gradient(mixin):
    '''css3 gradient'''
    def __init__(self, direction_start_end, pc_end = None):
        self.direction_start_end = self.cleanup(direction_start_end,
                                                'direction_start_end')
        self.pc_end = self.cleanup(pc_end, 'pc_end')
        
    def __call__(self, elem):
        val = Variable.pyvalue(self.direction_start_end)
        if not isinstance(val, RGBA) and isinstance(val, (tuple, list)):
            if len(val) != 3:
                raise ValueError('gradient must be a three element tuple.\
 Got "{0}".'.format(val))
            d,s,e = tuple((Variable.cssvalue(v) for v in val))
            if d in ('h','v','r','s'):
                self.decorate = getattr(self, d+'gradient')
            else:
                d = int(d)
                self.decorate = self.dgradient
            self.decorate(elem,d,s,e)
        else:
            # a simple scalar, just set the background
            elem['background'] = ascolor(val)
            
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
        
################################################# BCD - BACKGROUND-COLOR-DECO
class bcd(mixin):
    '''Background-color-text decoration and text shadow mixin. It
can be applied to any element. It forms the basis for the :class:`clickable`
mixin.
    
:parameter background: backgroud or css3 box-gradient
:parameter colour: colour
:parameter text_shadow: text shadow
:parameter text_decoration: text decoration 
'''
    def __init__(self, background = None, color = None, text_shadow = None,
                 text_decoration = None):
        if not isinstance(background, gradient):
            background = gradient(background)
        self.background = self.cleanup(background,'background')
        self.color = self.cleanup(color,'color')
        self.text_shadow = self.cleanup(text_shadow,'text_shadow')
        self.text_decoration = self.cleanup(text_decoration,'text_decoration')
    
    def __call__(self, elem):
        self.background(elem)
        elem['color'] = ascolor(self.color)
        elem['text-shadow'] = self.text_shadow
        elem['text_decoration'] = self.text_decoration
        
################################################# CLICKABLE        
class clickable(mixin):
    '''Defines the default, hover and active state.'''
    def __init__(self, default = None, hover = None, active = None, **kwargs):
        self.default = self.cleanup(default,'default',bcd)
        self.hover = self.cleanup(hover,'hover',bcd)
        self.active = self.cleanup(active,'active',bcd)
        
    def __call__(self, elem):
        if elem.tag.endswith(':link'):
            tag = elem.tag[:-5]
        else:
            tag = elem.tag
        if self.default:
            self.default(elem)
        if self.hover:
            yield cssa(':hover', self.hover, parent = elem)
        if self.active:
            yield cssa(':active', self.active, parent = elem)
            yield cssa('.active', self.active, parent = elem)
        
################################################# HORIZONTAL NAV
class horizontal_navigation(clickable):
    '''Horizontal navigation with ul and li tags'''
    def __init__(self, float = 'left', margin=0, height=None,
                 padding=None, secondary_padding =None,
                 secondary_with=None,
                 radius = None, box_shadow = None,
                 display_all = False, **kwargs):
        super(horizontal_navigation, self).__init__(**kwargs)
        if float not in ('left','right'):
            float = 'left'
        self.float = float
        self.margin = margin
        self.height = height or px(40)            
        self.secondary_with = secondary_with
        self.radius = g_radius(radius)
        self.box_shadow = shadow(box_shadow)
        self.display_all = display_all
        # padding
        self.padding = padding or secondary_padding
        self.secondary_padding = secondary_padding
        
    def __call__(self, elem):
        elem['display'] = 'block'
        elem['float'] = self.float
        elem['position'] = 'relative'
        if self.margin:
            elem['margin-'+self.float] = self.margin
        self.box_shadow(elem)
        padding = spacing(self.padding) if self.padding else\
                  spacing(px(10),px(10))
        secondary_padding = self.secondary_padding or padding
        line_height = self.height - padding.top - padding.bottom
        if line_height.value <= 0:
            raise ValueError('Nav has height to low compared to paddings')
        #
        default = self.default or bcd()
        hover = self.hover or bcd() 
        active = self.active or bcd()
        # li elements in the main navigation ( > li)
        yield cssb('li',
                   clickable(hover=bcd(background=hover.background),
                             active=bcd(background=active.background)),
                   parent = elem,
                   display = 'block',
                   float = 'left')
        # The sub lists
        yield css('ul',
                  self.radius,
                  gradient(hover.background, 100),
                  parent = elem,
                  position='absolute',
                  padding=self.secondary_padding,
                  top = self.height,
                  width = self.secondary_with,
                  display = self.display_all)
        # The anchors
        yield css('a',
                  default,
                  parent = elem,
                  display = 'inline-block',
                  float = 'none',
                  line_height = line_height,
                  padding = self.padding)
        # The sub lists li
        yield css('li',
                  cssa(':hover',
                       css('a', hover),
                       cssb('ul', display = 'block')),
                  cssa('.active a', active),
                  parent = elem,
                  position = 'relative')
                
        
################################################################################
##    BATTERY INCLUDED GENERATORS
################################################################################
        
################################################# INCLUDE CSS

class include_css(generator):
    '''Include one or more css resources'''
    def __init__(self, *paths):
        self.paths = paths
        
    def __call__(self):
        for path in self.paths:
            if not path.startswith('http'):
                path = cssv.MEDIAURL + path
            
   
################################################# FIXED GRID
class grid(generator):
    '''Generate a grid layout given a number of *columns*, a *span*
size for one column and the *gutter* size between columns.'''
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
                   clearfix())
    
    def container(self, tag):
        return css(tag,
                   clearfix(),
                   width = px(self.width),
                   margin_left = 'auto',
                   margin_right = 'auto')
        
    def __call__(self):
        scol = '-{0}'.format(self.columns)
        row = self.row('.row' + self.grid_class + scol)
        yield row
        for s in range(1,self.columns+1):
            w = '{0}{1}'.format(s*self.span + (s-1)*self.gutter,self.unit)
            yield cssb('.span{1}'.format(row,s), parent=row, width=w)
        yield cssb('[class*="span"]'.format(row),
                   parent = row,
                   float='left',
                   margin_left='{0}{1}'.format(self.gutter,self.unit))
        yield cssb('[class*="span"]:first-child',
                   parent=row,
                   margin_left=0)
        yield self.container('.grid-container'+self.grid_class+scol)
        
        

################################################# FLUID GRID        
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
        self.span = round((100 - columns*gutter)/columns, 4)
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
        
    #def __call__(self):
    #    elems = list(super(fluidgrid,self).__call__())
    #    row = elems[0]
    #    for elem in elems:
    #        yield elem
    #    yield cssb('[class*="span"]:first-child',
    #               parent=row,
    #               margin_left=0)
