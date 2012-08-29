import colorsys
from collections import namedtuple

from .base import ispy3k, Variable, ProxyVariable, lazy, clamp, native_str,\
                     to_string

if not ispy3k:  # pragma: no cover
    from itertools import izip
    zip = izip


__all__ = ['RGBA', 'color', 'lighten', 'darken', 'mix_colors']

clamprgb = lambda v : int(clamp(round(v),255))

hex2 = lambda v : '0'+hex(v)[2:] if v < 16 else hex(v)[2:]

HSLA = namedtuple('HSLA','h s l alpha')
HSVA = namedtuple('HSVA','h s v alpha')
string_colors = frozenset(('transparent', 'inherit'))
    

class RGBA(namedtuple('RGBA','r g b alpha')):
    '''CSS3 red-green-blue & alpha color definition. It contains conversions
to and from HSL_ and HSV representations.

.. attribute:: r

    red light (0 to 255)

.. attribute:: g

    green light (0 to 255)
    
.. attribute:: b

    blue light (0 to 255)    

.. attribute:: alpha

    opacity level (0 to 1)
    
.. _HSL: http://en.wikipedia.org/wiki/HSL_and_HSV
'''
    def __new__(cls, r, g, b, alpha = 1):
        return super(RGBA,cls).__new__(cls,clamprgb(r),clamprgb(g),clamprgb(b),
                                       clamp(alpha))
    
    def __unicode__(self):
        return to_string(self.tocss())
    
    def __str__(self):
        return native_str(self.tocss())
    __repr__ = __str__
    
    def __add__(self, other):
        if isinstance(other, self.__class__):
            return self.mix(self,other)
        else:
            raise ValueError('Cannot add "{0}" to "{1}"'.format(self,other))
        
    def __sub__(self, other):
        if isinstance(other, self.__class__):
            r = tuple((2*v1-v2 for v1,v2 in zip(self,other))) 
            return self.__class__(*r)
        else:
            raise ValueError('Cannot subtract "{0}" to "{1}"'
                             .format(self,other))
        
    def tocss(self):
        '''Convert to a css string representation.'''
        if self.alpha < 1.0:
            return 'rgba(' + ', '.join((str(v) for v in self)) + ')'
        else:
            return '#' + ''.join((hex2(v) for v in self[:3]))
        
    def tohsla(self):
        '''Convert to HSL representation (hue, saturation, lightness).
Note all values are number between 0 and 1. Therefore for the hue, to obtain
the angle value you need to multiply by 360.

:rtype: a four elements tuple containing hue, saturation, lightness, alpha'''
        h,l,s = colorsys.rgb_to_hls(self.r/255., self.g/255., self.b/255.)
        return HSLA(h, s, l, self.alpha)
    
    def tohsva(self):
        '''Convert to HSV representation (hue, saturation, value). This
is also called HSB (hue, saturation, brightness).
Note all values are number between 0 and 1. Therefore for the hue, to obtain
the angle value you need to multiply by 360.

:rtype: a four elements tuple containing hue, saturation, value, alpha'''
        h,s,v = colorsys.rgb_to_hsv(self.r/255., self.g/255., self.b/255.)
        return HSVA(h, s, v, self.alpha)
    
    def darken(self, weight):
        '''Darken the color by a given *weight* in percentage. It return a
new :class:`RGBA` color with lightness decreased by that amount.'''
        h, s, l, a = self.tohsla();
        l = clamp(l - 0.01*weight);
        return self.fromhsl((h, s, l, a))
    
    def lighten(self, weight):
        '''Lighten the color by a given *weight* in percentage. It return a
new :class:`RGBA` color with lightness increased by that amount.'''
        h, s, l, a = self.tohsla();
        l = clamp(l + 0.01*weight);
        return self.fromhsl((h, s, l, a))
    
    def clone(self, r = None, g = None, b = None, alpha = None):
        return self.__class__(self.r if r is None else r,
                              self.g if g is None else g,
                              self.b if b is None else b,
                              self.alpha if alpha is None else alpha)
        
    @classmethod
    def fromhsl(cls, hsla):
        h, s, l, alpha = hsla
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return cls(255*r, 255*g, 255*b, alpha)
    
    @classmethod
    def make(cls, col, alpha = None):
        if isinstance(col, cls):
            if alpha is None:
                return col
            else:
                return col.clone(alpha = alpha)
        else:
            if isinstance(col,(list,tuple)):
                if len(col) == 4:
                    alpha = col[3] if alpha is None else alpha
                    col = col[:3]
                rgb = tuple(col)
            else:
                col = str(col)
                if col in string_colors:
                    return col
                elif col.startswith('#'):
                    col = col[1:]
                if len(col) == 6:
                    rgb = tuple((int(col[2*i:2*(i+1)],16) for i in range(3)))
                elif len(col) == 3:
                    rgb = tuple((int(2*col[i],16) for i in range(3)))
                else:
                    raise ValueError('Could not recognize color "%s"' % col)
            rgb += (1 if alpha is None else alpha,)
            return cls(*rgb)
        
    @classmethod
    def mix(cls, rgb1, rgb2, weight = 50):
        p = clamp(0.01*weight)
        w = 2*p - 1;
        a = rgb1.alpha - rgb2.alpha
        w1 = ((w if w*a == -1 else (w+a)/(1+w*a)) + 1) / 2.0
        w2 = 1 - w1;
        return cls(w1*rgb1.r + w2*rgb2.r,
                   w1*rgb1.g + w2*rgb2.g,
                   w1*rgb1.b + w2*rgb2.b,
                   p*rgb1.alpha + (1-p)*rgb2.alpha)
        

class Color(Variable):
    '''A :class:`Variable` wrapping a :class:`RGBA` color.'''
    @classmethod
    def from_value(cls, col, alpha=None, **kwargs):
        col = RGBA.make(col, alpha)
        if isinstance(col, RGBA):
            return cls(col)
        else:
            return col
        
    def _unit(self):
        return 'color'
    
    @property
    def r(self):
        return self.value.r
    
    @property
    def g(self):
        return self.value.g
    
    @property
    def b(self):
        return self.value.b
    
    @property
    def alpha(self):
        return self.value.alpha
    
    def tocss(self):
        return self.value.tocss()
    
    def tohsla(self):
        return self.value.tohsla()
    
    def tohsva(self):
        return self.value.tohsva()
    

################################################################################
##    color factory
color = lambda col, alpha=None, **kwargs: Color.make(col, alpha=alpha, **kwargs)

def darken(col, weight):
    c = Color.make(col)
    if isinstance(c, ProxyVariable):
        return lazy(lambda : color(c.value).value.darken(weight))
    else:
        return c.value.darken(weight)

def lighten(col, weight):
    c = Color.make(col)
    if isinstance(c, ProxyVariable):
        return lazy(lambda : color(c.value).value.lighten(weight))
    else:
        return c.value.lighten(weight)

def mix_colors(col1, col2, weight=50):
    c1 = Color.make(col1)
    c2 = Color.make(col2)
    if isinstance(c1, ProxyVariable) or isinstance(c2, ProxyVariable):
        return lazy(lambda : RGBA.mix(c1.value, c2.value, weight))
    else:
        return RGBA.mix(c1.value, c2.value, weight)
    