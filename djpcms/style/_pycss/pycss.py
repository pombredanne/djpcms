'''A css generator in python.
No templating involved, just python classes, functions and little magic.
'''
VERSION = (0, 1, 0)

################################################################################
__version__ = '.'.join(map(str,VERSION))
__license__  = "BSD"
__author__ = "Luca Sbardella"
__contact__ = "luca.sbardella@gmail.com"
__homepage__ = "http://djpcms.com/"
################################################################################

import sys
import argparse
from uuid import uuid4
from copy import copy
from datetime import datetime
from inspect import isgenerator
from collections import OrderedDict
from importlib import import_module

__all__ = ['css', 'cssa', 'cssb', 'cssc',
           'var', 'color', 'mixin', 'generator',
           'cssv', 'lazy', 'cssvalue', 'px', 'em', 'pc',
           'shadow', 'radius', 'gradient',
           'clearfix', 'fixtop',
           'grid', 'fluidgrid']

if sys.version_info >= (3,):    # pragma: no cover
    from io import StringIO
    itervalues = lambda d : d.values()
    iteritems = lambda d : d.items()
    
    class UnicodeMixin(object):
        
        def __unicode__(self):
            return '{0} object'.format(self.__class__.__name__)
        
        def __str__(self):
            return self.__unicode__()
        
        def __repr__(self):
            return '%s: %s' % (self.__class__.__name__,self)
else:   # pragma: no cover
    from cStringIO import StringIO
    range = xrange
    
    class UnicodeMixin(object):
        
        def __unicode__(self):
            return unicode('{0} object'.format(self.__class__.__name__))
        
        def __str__(self):
            return self.__unicode__().encode()
        
        def __repr__(self):
            return '%s: %s' % (self.__class__.__name__,self)


def cssvalue(o, raw = False):
    if isinstance(o, lazy):
        return o.raw_value() if raw else o.value
    elif hasattr(o,'__call__'):
        return o()
    else:
        return o

def clamp(val):
    return min(1.0, max(0.0, val))

def itertuple(mapping):
    if isinstance(mapping,dict):
        return iteritems(mapping)
    else:
        return mapping

    
class lazy(UnicodeMixin):
    '''A lazy css value'''
    def __init__(self, value):
        self._value = value
    
    def _get_value(self):
        return self._get(False)
    def _set_value(self, value):
        return self._set(value)
    value = property(_get_value,_set_value)
    
    def __unicode__(self):
        return '{0}'.format(self.value)
    
    def raw_value(self):
        '''Return the raw value for this :class:`lazy` object.'''
        return self._get(True)
    
    def _get(self, raw):
        return cssvalue(self._value, raw)
    
    def _set(self, value):
        self._value = value
    
    def _op(self, other, ope):
        val = self.raw_value()
        oval = other.raw_value() if isinstance(other, lazy) else other
        res = ope(val,oval)
        self.value = res
        rval, self.value = self.value, val
        return rval
        
    def __add__(self, other):
        return self._op(other, lambda a,b: a+b)
    
    def __sub__(self, other):
        return self._op(other, lambda a,b: a-b)
    
    def __mul__(self, other):
        return self._op(other, lambda a,b: a*b)
    
    def __div__(self, other):
        return self._op(other, lambda a,b: a/b)
    
    def __eq__(self, other):
        return self.value == cssvalue(other)
    
    def __lt__(self, other):
        return self.value < cssvalue(other)


class px(lazy):
    def __init__(self, value, unit = 'px'):
        super(px,self).__init__(value)
        self.unit = unit
    
    def _get(self, raw):
        v = super(px,self)._get(raw)
        return v if raw else '{0}{1}'.format(v,self.unit)
        
pc = lambda v: px(v,'%')
em = lambda v: px(v,'em')
    
    
class mixin(UnicodeMixin):
    '''A css *mixin* is a generator of :class:`css` and other
:class:`mixin` elements. All :class:`mixin` must implement the
callable method.'''
    def __call__(self, elem):
        raise NotImplementedError()
    

class generator(UnicodeMixin):
    '''A generator is a factory of :class:`css` elements.'''

    def __new__(cls, *args, **kwargs):
        o = super(generator,cls).__new__(cls)
        o.id = str(uuid4())[:8]
        CSS._body._children[o.id] = o
        return o
        
            
class CSS(UnicodeMixin):
    _body = None
    parent_relationship = 'child'
    parent_link = {'child': ' ',
                   'attribute': ':',
                   'bigger': ' > ',
                   'klass': ''}
    as_clone = False
    def __init__(self, tag):
        self._tag = tag
        self._children = OrderedDict()
        self._parent = None
        self._attributes = []
        self.mixins = []
        if tag == 'body':
            self.__class__._body = self
        
    def _setup(self, *components, **attributes):
        parent = attributes.pop('parent',None)
        self.parent_relationship = attributes.pop('parent_relationship',
                                                  self.parent_relationship)
        self._attributes.extend((itertuple(attributes.pop('data',{}))))
        for name,value in iteritems(attributes):
            self[name] = value
        self.parent = parent
        for c in components:
            if isinstance(c, CSS):
                c.parent = self
            elif isinstance(c, mixin):
                self.mixins.append(c)
            else:
                raise TypeError('"{0}" is not a valid type'.format(c))
    
    def __setitem__(self, name, value):
        if value is not None:
            name = name.replace('_','-')
            self._attributes.append((name,value))
    
    def __getitem__(self, name):
        raise NotImplementedError('cannot get item')
    
    def __iter__(self):
        elem = self.clone()
        mixins = []
        for mixin in self.mixins:
            res = mixin(elem)
            if res:
                mixins.extend(res)
        yield elem
        for mchild in itervalues(elem._children):
            for child in mchild:
                yield child
        for mchild in itervalues(elem._body._children):
            for child in mchild:
                if child is not elem:
                    yield child
    
    def clone(self):
        cls = self.__class__
        q = cls.__new__(cls)
        d = self.__dict__.copy()
        d['_attributes'] = copy(d['_attributes'])
        d['_children'] = OrderedDict()
        d['as_clone'] = True
        d['_body'] = CSS('body')
        q.__dict__ = d
        return q
        
    @property
    def tag(self):
        return self._full_tag(self._tag)

    def _full_tag(self, tag):
        if self._parent and self._parent.tag != 'body':
            c = self.parent_link[self.parent_relationship]
            return self._parent.tag + c + tag
        else:
            return tag
            
    def _get_parent(self):
        return self._parent
    def _set_parent(self, parent):
        # Get the element if available
        if self.tag == 'body':
            if self.parent:
                raise ValueError('Body cannot have parent')
            return
        # Just in case we switch parent
        if self._parent:
            q = self.parent._children.get(self._tag)
            if q:
                for i, c in enumerate(list(q)):
                    if c is self:
                        q.pop(i)
        self._parent = parent or self._body
        q = self._parent._children.get(self._tag)
        if q is None:
            q = []
            self._parent._children[self._tag] = q
        q.append(self)
    parent = property(_get_parent,_set_parent)
    
    def alltags(self):
        '''Generator of all tags in the css component.'''
        tags = self._tag.split(',')
        for tag in tags:
            if tag:
                yield self._full_tag(tag)
                
    def _stream(self):
        yield ',\n'.join(self.alltags()) + ' {'
        for k,v in self._attributes:
            v = cssvalue(v)
            if v is not None:
                yield '    {0}: {1};'.format(k,v)
        yield '}'
        
    def stream(self):
        for elem in self:
            yield '\n'.join(elem._stream())

    def __unicode__(self):
        return '\n\n'.join(self.stream())
    
    def render(self, stream=None):
        '''Render the :class:`css` component and all its children'''
        stream = stream if stream is not None else StringIO()
        stream.write(self.__unicode__())
        for mchild in itervalues(self._children):
            if isinstance(mchild, generator):
                mchild = mchild()
            for child in mchild:
                stream.write('\n\n')
                child.render(stream)
    

CSS('body')
class css:
    
    def __call__(self, tag, *components, **attributes):
        if tag == 'body':
            elem = CSS._body
        else:
            elem = CSS(tag)
        elem._setup(*components, **attributes)
        return elem

    def get(self, name):
        return CSS._body._children.get(name)
        
    def render(self, media_url = None, charset = 'utf-8'):
        now = datetime.now()
        stream = StringIO()
        intro = '''\
/*
------------------------------------------------------------------
------------------------------------------------------------------
Created by pycss  {0}
------------------------------------------------------------------
------------------------------------------------------------------ */

'''.format(now)
        stream.write(intro)
        CSS._body.render(stream)
        return stream.getvalue()

css = css()
def cssa(*args, **kwargs):
    kwargs['parent_relationship'] = 'attribute'
    return css(*args, **kwargs)
def cssb(*args, **kwargs):
    kwargs['parent_relationship'] = 'bigger'
    return css(*args, **kwargs)
def cssc(*args, **kwargs):
    kwargs['parent_relationship'] = 'klass'
    return css(*args, **kwargs)

hex2 = lambda v : '0'+hex(v)[2:] if v < 16 else hex(v)[2:]


class color(lazy):
    '''Utility for handling colors'''
    def __init__(self, col, alpha = 1):
        self._set(col)
        self.alpha = alpha
        
    def tocss(self):
        if self.alpha < 1.0:
            return 'rgba(' + ', '.join((str(rgb) for rgb in self.rgb))\
                           + ', ' + str(self.alpha) + ')'
        else:
            return '#' + ''.join((hex2(v) for v in self.rgb))
    
    def _get(self, raw):
        if raw:
            return self
        else:
            return self.tocss()
        
    def _set(self, value):
        if isinstance(value, color):
            self.rgb = value.rgb
            self.alpha = value.alpha
        else:
            alpha = 1
            rgb = value
            if isinstance(rgb,(list,tuple)):
                if len(rgb) == 4:
                    alpha = rgb[3]
                    rgb = rgb[:3]
                elif len(rgb) != 3:
                    raise ValueError('Cannot assign color "{0}"'.format(rgb))
            else:
                col = str(value)
                if col.startswith('#'):
                    col = col[1:]
                if len(col) == 6:
                    rgb = tuple((int(col[2*i:2*(i+1)],16) for i in range(3)))
                elif len(col) == 3:
                    rgb = tuple((int(2*col[i],16) for i in range(3)))
                else:
                    raise ValueError('Could not recognize color "{0}"'\
                                     .format(rgb))
            self.rgb = rgb
            self.alpha = alpha
    
    def tohsl(self):
        '''Convert to HSL representation (hue, saturation, lightness).'''
        r,g,b = tuple((v/255. for v in self.rgb))
        ma, mi = max(r, g, b), min(r, g, b)
        l, d = (ma + mi) / 2, ma - mi;
        if ma == mi:
            h = s = 0
        else:
            s = d / (2 - ma - mi) if l > 0.5 else d / (ma + mi)
            if r == ma:
                h = (g - b) / d + (6 if g < b else 0)
            elif g == ma:
                h = (b - r) / d + 2
            else:
                h = (r - g) / d + 4
            h /= 6
        return {'h': h*360, 's': s, 'l': l, 'a': self.alpha}
    
    @classmethod
    def as_color(cls, col):
        if not isinstance(col,cls):
            col = cls(col)
        return col
    
    @classmethod
    def fromhsl(cls, hsl):
        h = (hsl['h'] % 360) / 360
        s, l, a = hsl['s'], hsl['l'], hsl['a']
        m2 = l * (s + 1) if l <= 0.5 else l + s - l * s
        m1 = l * 2 - m2;
        hue = cls.hue
        return cls((int(hue(h + 1/3, m1, m2)*255),
                    int(hue(h, m1, m2)*255),
                    int(hue(h - 1/3, m1, m2)*255)), a);
    
    @classmethod
    def hue(cls, h, m1, m2):
        h = h + 1 if h < 0 else (h - 1 if h > 1 else h)
        if h * 6 < 1:
            return m1 + (m2 - m1) * h * 6
        elif h * 2 < 1:
            return m2
        elif h * 3 < 2:
            return m1 + (m2 - m1) * (2/3 - h) * 6
        else:
            return m1
        
    @classmethod
    def mix(cls, color1, color2, weight):
        p = 0.01*weight;
        w = p * 2 - 1;
        a = color1.alpha - color2.alpha
        w1 = ((w if w * a == -1 else (w + a) / (1 + w * a)) + 1) / 2.0
        w2 = 1 - w1;
        rgb = (color1.rgb[0] * w1 + color2.rgb[0] * w2,
               color1.rgb[1] * w1 + color2.rgb[1] * w2,
               color1.rgb[2] * w1 + color2.rgb[2] * w2)
        alpha = color1.alpha * p + color2.alpha * (1 - p);
        return cls(rgb, alpha)
    
    @classmethod
    def darken(cls, col, weight):
        col = cls.as_color(col)
        hsl = col.tohsl();
        hsl['l'] = clamp(hsl['l'] - weight / 100.0);
        return cls.fromhsl(hsl);
        

class var(lazy):
    '''A variable holds several values for different styles.
    
.. attribute:: name

    variable name
'''
    def __init__(self, hnd, name, value):
        super(var, self).__init__(value)
        self.hnd = hnd
        self.name = name
        self._values = {}
        
    @property
    def theme(self):
        return self.hnd.theme()
    
    def _get(self, raw):
        return cssvalue(self._values.get(self.theme, self._value), raw)
    
    def _set(self, value):
        theme = self.theme
        if theme in self._values:
            self._values[theme] = value
        else:
            self._value = value
    
    
class theme(object):
    
    def __init__(self, hnd, theme):
        self.__dict__['hnd'] = hnd
        self.__dict__['theme'] = theme
    
    def __repr__(self):
        return self.__dict__['theme']
    
    def __setattr__(self, name, value):
        getattr(self.hnd, name).value = value
        
    
class Variables(object):
    '''Holder of variables'''
    def set_theme(self, theme):
        self.__dict__['_theme'] = theme
        
    def theme(self):
        return self.__dict__.get('_theme')
    
    def theme_setter(self, theme_name):
        return theme(self, theme_name)
        
    def declare(self, name, value):
        '''Declare or update a variable with *default* value.'''
        
        if name and (value is None or\
                isinstance(value,(str,float,int,list,tuple,dict,lazy))):
            name = name.lower()
            d = self.__dict__
            if name in d:
                d[name].value = value
            else:
                d[name] = var(self, name, value)
            return d[name]
    
    def __iter__(self):
        d = self.__dict__
        for name in sorted(d):
            val = d[name]
            if isinstance(val,var):
                yield val
                
    def __contains__(self, name):
        return name.lower() in self.__dict__
    
    def __setattr__(self, name, value):
        self.declare(name, value)
    
    def __getattr__(self, name):
        name = name.lower()
        if name not in self.__dict__:
            raise AttributeError('Attribute {0} not available'.format(name))
        else:
            return self.__dict__[name]
        
    def declare_from_module(self, module):
        '''Declare variables from a python *module*.'''
        for name in dir(module):
            if name.startswith('_'):
                continue
            if name == name.lower():
                val = getattr(module, name)
                self.declare(name, val)

        
cssv = Variables()
jquery_theme_mapping = {}   

################################################################################
##    BATTERY INCLUDED MIXINS
################################################################################

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
        elem['zindex'] = cssvalue(self.zindex)
        
            
################################################# CSS3 BOX SHADOW
class shadow(mixin):
    def __init__(self, shadow):
        self.shadow = shadow
        
    def __call__(self, elem):
        shadow = cssvalue(self.shadow)
        elem['-webkit-box-shadow'] = shadow
        elem['   -moz-box-shadow'] = shadow
        elem['        box-shadow'] = shadow
        
################################################# CSS3 RADIUS        
class radius(mixin):
    def __init__(self, radius):
        self.radius = radius
        
    def __call__(self, elem):
        r = cssvalue(self.radius)
        elem['-webkit-border-radius'] = r
        elem['   -moz-border-radius'] = r
        elem['        border-radius'] = r

################################################# CSS3 GRADIENT
class gradient(mixin):
    def __init__(self, direction_start_end):
        self.direction_start_end = direction_start_end
        
    def __call__(self, elem):
        d,s,e = cssvalue(self.direction_start_end)
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
        

################################################################################
##    BATTERY INCLUDED GENERATORS
################################################################################
        
################################################# FIXED GRID
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
        
        
def jqueryui(context, loader, theme):
    theme = theme or 'smooth'
    jtheme = jquery_theme_mapping.get(theme,theme)
    base  = 'jquery-ui-css/{0}/'.format(jtheme)
    data = loader.render(base + 'jquery-ui.css')
    toreplace = 'url(images'
    media_url = context['MEDIA_URL']
    replace = 'url({0}djpcms/'.format(media_url) + base + 'images'
    lines = data.split(toreplace)
    def jquery():
        yield lines[0]
        for line in lines[1:]:
            p = line.find(')')
            if p:
                line = replace + line
            else:
                line = toreplace + line
            yield line
    return ''.join(jquery())


def csscompress(stream):
    return stream

def printf(v):  # pragma: no cover
    print(v)
    
def dump_theme(theme, target, show_variables = False, minify = False,
               verbose = True):
    log = printf if verbose else lambda v: v
    cssv.set_theme(theme)
    if show_variables:
        log('STYLE: {0}'.format(cssv.theme() or 'Default'))
        section = None
        for var in cssv:
            sec = var.name.split('_')[0]
            if sec != section:
                section = sec
                log('')
                log(section)
                log('==================================================')
            log('{0}: {1}'.format(var.name,var.value))
    else:
        data = css.render()
        f = open(target,'w')
        f.write(data)
        f.close()
        log('Saved style on file "{0}"'.format(target))
    
    
def main(verbose = True):
    argparser = argparse.ArgumentParser('Python CSS generator')

    # TODO Add debug information output switch.
    argparser.add_argument('source',
                           nargs='*',
                           help='Dotted path to source files or directories.')
    argparser.add_argument('-t', '--theme',
                           default=None,
                           help='Theme name')
    argparser.add_argument('-o', '--output',
                           help='File path to store CSS into.',
                           default='pycss.css')
    argparser.add_argument('-v','--variables',
                           action='store_true',
                           default=False,
                           help='List all variables values')
    argparser.add_argument('-m','--minify',
                           action='store_true',
                           default=False,
                           help='Minify output file')
    
    opts = argparser.parse_args()
    for source in opts.source:
        mod = import_module(source)
    
    dump_theme(opts.theme, opts.output, opts.variables, opts.minify,
               verbose = verbose)    
    