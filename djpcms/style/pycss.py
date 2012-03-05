'''Script for writing css files in a pythonic way.
Not templating, just python functions and magic.

The main classes here are :class:`css` and :class:`mixin`.
'''
from uuid import uuid4
from copy import copy
from datetime import datetime
from inspect import isgenerator

from djpcms.utils.py2py3 import UnicodeMixin, iteritems, itervalues, StringIO,\
                                native_str, range
from djpcms.utils.structures import OrderedDict

__all__ = ['css', 'cssc', 'cssa',
           'var', 'color', 'mixin', 'generator',
           'cssv', 'deval', 'lazy']


def deval(o):
    return o.value if isinstance(o,var) else o

def clamp(val):
    return min(1.0, max(0.0, val))

def itertuple(mapping):
    if isinstance(mapping,dict):
        return iteritems(mapping)
    else:
        return mapping
    
class lazy():
    def __init__(self, callable):
        self.callable = callable
    
    def __call__(self):
        return self.callable()

    
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
    parent_link = {'child': ' ', 'attribute': ':', 'klass': ''}
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
            v = deval(v) 
            if hasattr(v,'__call__'):
                v = v()
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
        
    def render(self, media_url, charset = 'utf-8'):
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
def cssc(*args, **kwargs):
    kwargs['parent_relationship'] = 'klass'
    return css(*args, **kwargs)
def cssa(*args, **kwargs):
    kwargs['parent_relationship'] = 'attribute'
    return css(*args, **kwargs)

hex2 = lambda v : '0'+hex(v)[2:] if v < 16 else hex(v)[2:]


class color(UnicodeMixin):
    '''Utility for handling colors'''
    def __init__(self, col, alpha = 1):
        if isinstance(col,list):
            self.rgb = tuple(col)
        elif isinstance(col,tuple):
            self.rgb = col
        else:
            col = str(col)
            if col.startswith('#'):
                col = col[1:]
            if len(col) == 6:
                self.rgb = tuple((int(col[2*i:2*(i+1)],16) for i in range(3)))
            elif len(col) == 3:
                self.rgb = tuple((int(2*col[i],16) for i in range(3)))
            else:
                raise ValueError('Could not recognize color "{0}"'.format(col))
        self.alpha = alpha
        
    def tocss(self):
        if self.alpha < 1.0:
            return 'rgba(' + ', '.join((str(rgb) for rgb in self.rgb))\
                           + ', ' + str(self.alpha) + ');'
        else:
            return '#' + ''.join((hex2(v) for v in self.rgb))
    
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
    
    def __unicode__(self):
        return self.tocss()
    
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
        

class var(UnicodeMixin):
    '''A variable holds several values for different styles.
    
.. attribute:: name

    variable name
'''
    def __init__(self, hnd, name, value):
        self.hnd = hnd
        self.name = name
        self.default_value = value
        self.values = {}
        
    @property
    def theme(self):
        return self.hnd.theme()
    
    @property
    def value(self):
        return self.values.get(self.theme,self.default_value)
    
    def __unicode__(self):
        value = self.value
        if isinstance(value,mixin):
            value = value()
        return '{0}'.format(value)
    
    def __add__(self, other):
        return self.value + deval(other)
    
    def __sub__(self, other):
        return self.value - deval(other)
    
    def __mul__(self, other):
        return self.value * deval(other)
    
    def __div__(self, other):
        return self.value / deval(other)
    
    def __eq__(self, other):
        return self.value == deval(other)
    
    def __lt__(self, other):
        return self.value < deval(other)
    
    
class theme(object):
    
    def __init__(self, hnd, theme):
        self.__dict__['hnd'] = hnd
        self.__dict__['theme'] = theme
    
    def __repr__(self):
        return self.__dict__['theme']
    
    def __setattr__(self, name, value):
        getattr(self.hnd, name).values[self.theme] = value
        
    
class Variables(object):
    
    def set_theme(self, theme):
        self.__dict__['_theme'] = theme
        
    def theme(self):
        return self.__dict__.get('_theme')
    
    def theme_setter(self, theme_name):
        return theme(self, theme_name)
        
    def declare(self, name, default):
        name = name.lower()
        if name in self.__dict__:
            raise KeyError('variable {0} already declared'.format(name))
        self.__dict__[name] = var(self, name, default)
    
    def __iter__(self):
        d = self.__dict__
        for name in sorted(d):
            val = d[name]
            if isinstance(val,var):
                yield val
                
    def set_or_declare(self, name, value):
        if name and (value is None or\
                      isinstance(value,(str,float,int,list,tuple,dict,lazy))):
            name = name.lower()
            if name in self.__dict__:
                self.__dict__[name].default_value = value
            else:
                self.__dict__[name] = var(self,name,value)
            
    def __contains__(self, name):
        return name.lower() in self.__dict__
    
    def __setattr__(self, name, value):
        name = name.lower()
        if name not in self.__dict__:
            raise AttributeError('Attribute {0} not available'.format(name))
        else:
            self.__dict__[name].default_value = value
    
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
                self.set_or_declare(name, val)

        
cssv = Variables()
jquery_theme_mapping = {}   

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

