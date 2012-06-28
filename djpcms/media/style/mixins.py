'''Useful mixins and generators'''
import os
from uuid import uuid4

from djpcms.utils.httpurl import to_string

from .base import *
from .colorvar import *

__all__ = ['opacity',
           'clearfix',
           'fixtop',
           'unfixtop',
           'border',
           'shadow',
           'radius',
           'gradient',
           'placeholder',
           'bcd',
           'clickable',
           'horizontal_navigation',
           # generators
           'css_include',
           'grid',
           'gridfluid',
           'fontface']
 
    
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
        cssa(':before,:after',
             parent = elem,
             display = 'table',
             content = '""')
        cssa(':after',
             parent = elem,
             clear = 'both')
            
################################################# FIXTOP
class fixtop(mixin):
    '''Fix an element at the top of the page.'''
    def __init__(self, zindex = 2000):
        self.zindex = self.cleanup(zindex, 'zindex')
            
    def __call__(self, elem):
        elem['left'] = 0
        elem['top'] = 0
        elem['right'] = 0
        elem['position'] = 'fixed'
        elem['z_index'] = Variable.cssvalue(self.zindex)
        

class unfixtop(mixin):
    def __call__(self, elem):
        elem['left'] = 'auto'
        elem['top'] = 'auto'
        elem['right'] = 'auto'
        elem['position'] = 'static'
        elem['z_index'] = 'auto'
        
################################################# CSS BORDER
class border(mixin):
    def __init__(self, color=None, style=None, width=None):
        self.color = color
        self.style = style
        self.width = width
    
    def __call__(self, elem):
        color = self.color
        if color:
            style = self.style or 'solid'
            width = self.width or px(1)
            elem['border'] = '%s %s %s' % (width,style,color)
        
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
    '''css3 border radius.'''
    def __init__(self, radius):
        self.radius = self.cleanup(radius, 'radius')
        
    def __call__(self, elem):
        r = Variable.cssvalue(self.radius)
        if r is not None:
            elem['-webkit-border-radius'] = r
            elem['   -moz-border-radius'] = r
            elem['        border-radius'] = r
g_radius = radius

################################################# CSS3 GRADIENT
class gradient(mixin):
    '''css3 gradient

.. attribute:: direction_start_end

    three elements tuple for direction ('h', 'v', 'r' or 's')
'''
    def __new__(cls, direction_start_end, pc_end=None):
        if isinstance(direction_start_end, gradient):
            return direction_start_end
        else:
            o = super(gradient,cls).__new__(cls)
            o.direction_start_end = o.cleanup(direction_start_end,
                                              'direction_start_end')
            o.pc_end = o.cleanup(pc_end, 'pc_end')
            return o
        
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
        #
        # FF 3.6+
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
        #
        # IE9 and down
        elem['filter'] = "progid:DXImageTransform.Microsoft.gradient(\
startColorstr={0}, endColorstr={1}, GradientType={2})".format(s,e,t)
        #
        # Reset filters for IE
        elem['filter'] = 'progid:DXImageTransform.Microsoft.gradient'\
                         '(enabled = false)'
        
    def hgradient(self, elem, d, s, e):
        self._gradient(elem, 'left', s, e)
        
    def vgradient(self, elem, d, s, e):
        self._gradient(elem, 'top', s, e)
        

################################################# PLACEHOLDER
class placeholder(mixin):
    
    def __init__(self, color):
        self.color = color
    
    def __call__(self, elem):
        cssa('::-webkit-input-placeholder,'\
             ':-moz-placeholder,'\
             ':-ms-input-placeholder',
             parent=elem,
             color=self.color)
        
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
    def __init__(self, background=None, color=None, text_shadow=None,
                 text_decoration=None, **kwargs):
        self.background = gradient(background)
        self.color = self.cleanup(color, 'color')
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
        if self.default:
            self.default(elem)
        if self.hover:
            cssa(':hover', self.hover, parent=elem)
        if self.active:
            cssa(':active,.active', self.active, parent=elem)
        
################################################# HORIZONTAL NAVIGATION
class horizontal_navigation(clickable):
    '''Horizontal navigation with ul and li tags.
    
:parameter padding: the padding for the navigation anchors.'''
    def __init__(self,
                 float='left',
                 margin=0,
                 height=None,
                 padding=None,
                 secondary_default=None,
                 secondary_hover=None,
                 secondary_active=None,
                 secondary_padding=None,
                 secondary_width=None,
                 radius=None,
                 box_shadow = None,
                 display_all=False,
                 z_index=None,
                 **kwargs):
        super(horizontal_navigation, self).__init__(**kwargs)
        if float not in ('left','right'):
            float = 'left'
        self.float = float
        self.margin = margin
        self.height = height
        self.secondary_default = secondary_default
        self.secondary_hover = secondary_hover
        self.secondary_active = secondary_active
        self.secondary_width = secondary_width or px(120)
        self.radius = g_radius(radius)
        self.box_shadow = shadow(box_shadow)
        self.display_all = display_all
        # padding
        self.padding = padding or secondary_padding
        self.secondary_padding = secondary_padding or px(0)
        # Z index for subnavigations
        self.z_index = z_index or 1000
        
    def list(self, maker, parent, default, hover, active):
        return maker('li',
                  default.background,
                  cssb('a',
                       bcd(background='transparent',
                           color=default.color,
                           text_decoration=default.text_decoration,
                           text_shadow=default.text_shadow)),
                  cssa(':hover',
                       hover.background,
                       cssb('a',
                            bcd(color=hover.color,
                                text_decoration=hover.text_decoration,
                                text_shadow=hover.text_shadow)),
                       cssb('ul', display='block')),
                  cssa(':active, .active',
                       active.background,
                       cssb('a',
                            bcd(color=active.color,
                                text_decoration=active.text_decoration,
                                text_shadow=active.text_shadow))),
                  cursor='pointer',
                  parent=parent)
        
    def __call__(self, elem):
        elem['display'] = 'block'
        elem['float'] = self.float
        elem['position'] = 'relative'
        elem['padding'] = 0
        if self.margin:
            if self.float == 'left':
                elem['margin'] = spacing(0,self.margin,0,0)
            else:
                elem['margin'] = spacing(0,0,0,self.margin)
        self.box_shadow(elem)
        padding = spacing(self.padding) if self.padding else\
                  spacing(px(10),px(10))
        secondary_padding = self.secondary_padding or padding
        #
        default = self.default or bcd()
        hover = self.hover or bcd() 
        active = self.active or bcd()
        # li elements in the main navigation ( > li)
        li = self.list(cssb, elem, default, hover, active)
        li['display'] = 'block'
        li['float'] ='left'
        
        if self.height:
            line_height = self.height - padding.top - padding.bottom
            if line_height.value <= 0:
                raise ValueError('Nav has height to low compared to paddings')
        else:
            line_height = None
            
        # subnavigations
        default = self.secondary_default or default
        hover = self.secondary_hover or hover
        active = self.secondary_active or active
        ul = css('ul',
                  self.radius,
                  gradient(default.background, 100),
                  parent=elem,
                  cursor='default',
                  position='absolute',
                  margin=0,
                  padding=self.secondary_padding,
                  top=self.height,
                  width=self.secondary_width,
                  list_style='none',
                  list_style_image='none',
                  z_index=self.z_index)
        if not self.display_all:
            ul['display'] = 'none'
        # The sub lists li
        li = self.list(css, ul, default, hover, active)
        li['padding'] = 0
        li['margin'] = 0
        li['position'] = 'relative'
        li['border'] = 'none'
        li['width'] = 'auto'
        # the sub sub lists
        ulul = css('ul',
                   gradient(default.background, 100),
                   parent=li,
                   top=0,
                   position='absolute')
        if self.float == 'right':
            ul['right'] = 0
            ulul['left'] = 'auto'
            ulul['right'] = self.secondary_width
        else:
            ulul['left'] = self.secondary_width
            ulul['right'] = 'auto'
        # The anchor
        css('a',
            parent=elem,
            display='inline-block',
            float='none',
            line_height=line_height,
            padding=self.padding)

                
################################################# INCLUDE CSS
        
class css_include(mixin):
    '''Include one or more css resources'''
    def __init__(self, *paths):
        self.paths = paths
        self._code = to_string(uuid4())[:8]
        
    def __unicode__(self):
        return self._code
    
    def __call__(self, elem):
        for path in self.paths:
            if not path.startswith('http'):
                if os.path.isfile(path):
                    with open(path,'r') as f:
                        stream = f.read()
                else:
                    stream = path
            else:
                raise NotImplementedError('http fetching not yet implemented')
            css_stream(self._code, stream)
            
   
################################################# FIXED GRID
class grid(mixin):
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
    
    def __unicode__(self):
        return to_string(self.__class__.__name__+'-{0}'.format(self.columns)+\
                         self.extra_identity())
        
    def extra_identity(self):
        return '-'+str(int(self.width))
        
    def row(self, tag, **kwargs):
        m = '{0}{1}'.format(self.gutter,self.unit)
        return css(tag,
                   clearfix(),
                   **kwargs)
    
    def container(self, tag, **kwargs):
        return css(tag,
                   clearfix(),
                   width = px(self.width),
                   margin_left = 'auto',
                   margin_right = 'auto',
                   **kwargs)
        
    def __call__(self, elem):
        scol = '-{0}'.format(self.columns)
        row = self.row('.row'+self.grid_class+scol, parent=elem)
        for s in range(1,self.columns+1):
            w = '{0}{1}'.format(s*self.span + (s-1)*self.gutter,self.unit)
            cssb('.span{0}'.format(s), parent=row, width=w)
        cssb('[class*="span"]',
             parent=row,
             float='left',
             margin_left='{0}{1}'.format(self.gutter,self.unit))
        cssb('[class*="span"]:first-child',
             parent=row,
             margin_left=0)
        self.container('.grid-container'+self.grid_class+scol,
                       parent=elem)
        
        

################################################# FLUID GRID        
class gridfluid(grid):
    grid_class = '-fluid'
    unit = '%'
    def __init__(self, columns, gutter = 2.5641):
        if columns <=1:
            raise ValueError('Grid must have at least 2 columns')
        if gutter < 0:
            raise ValueError('gutter must be positive')
        self.columns = columns
        self.gutter = gutter
        self.span = round((100 - (columns-1)*gutter)/columns, 4)
        if self.span <= 0:
            raise ValueError('gutter too large')
    
    def extra_identity(self):
        return ''
    
    def row(self, tag, **kwargs):
        return css(tag,
                   clearfix(),
                   width = '100%',
                   **kwargs)
    
    def container(self, tag, **kwargs):
        return css(tag,
                   clearfix(),
                   padding_left = '20px',
                   padding_right = '20px',
                   **kwargs)
        
    #def __call__(self):
    #    elems = list(super(fluidgrid,self).__call__())
    #    row = elems[0]
    #    for elem in elems:
    #        yield elem
    #    yield cssb('[class*="span"]:first-child',
    #               parent=row,
    #               margin_left=0)


################################################# FONT-FACE 
class fontface(mixin):
    
    def __init__(self, base, svg=None):
        self.base = base
        self.svg = '#'+svg if svg else ''
        
    def __call__(self, elem):
        base = self.base
        if not base.startswith('http'):
            base = cssv.MEDIAURL + self.base
        elem['src'] = "url('{0}.eot')".format(base)
        elem['src'] = "url('{0}.eot?#iefix') format('embedded-opentype'), "\
                      "url('{0}.woff') format('woff'), "\
                      "url('{0}.ttf') format('truetype'), "\
                      "url('{0}.svgz{1}') format('svg'), "\
                      "url('{0}.svg{1}') format('svg')"\
                      .format(base, self.svg)