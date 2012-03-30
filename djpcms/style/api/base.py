import sys
import os
import argparse
import json
from itertools import chain
from uuid import uuid4
from copy import copy
from datetime import datetime
from inspect import isgenerator

from djpcms.utils.structures import OrderedDict


__all__ = ['css', 'cssa', 'cssb',
           'Variable', 'NamedVariable', 'mixin',
           'generator', 'cssv', 'lazy', 'px', 'em', 'pc',
           'spacing', 'dump_theme', 'main', 'Variables',
           'add_arguments']


nan = float('nan')
conversions = {}
ispy3k = sys.version_info >= (3,)

if ispy3k:    # pragma: no cover
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
    
    def native_str(s, encoding = 'utf-8'):
        if isinstance(s,bytes):
            return s.decode(encoding)
        return s
    
    def force_unicode(s, encoding = 'utf-8'):
        s = native_str(s,encoding)
        if not isinstance(s,str):
            s = str(s)
        return s
        
else:   # pragma: no cover
    from cStringIO import StringIO
    range = xrange
    itervalues = lambda d : d.itervalues()
    iteritems = lambda d : d.iteritems()
    
    class UnicodeMixin(object):
        
        def __unicode__(self):
            return unicode('{0} object'.format(self.__class__.__name__))
        
        def __str__(self):
            return self.__unicode__().encode()
        
        def __repr__(self):
            return '%s: %s' % (self.__class__.__name__,self)
        
    def native_str(s, encoding = 'utf-8'):
        if isinstance(s,unicode):
            return s.encode(encoding)
        return s
    
    def force_unicode(s, encoding = 'utf-8'):
        if not isinstance(s,unicode):
            if not isinstance(s,bytes):
                s = bytes(s)
            s = s.decode(encoding)
        return s

def clamp(val, maxval = 1):
    return min(maxval, max(0, val))

def div(self,other):
    return self._op(other, lambda a,b: a/float(b),
                    supported_types = (int,float))
    
    
class Variable(UnicodeMixin):
    '''A general variable.
    
.. attribute:: value

    The value to be displayed in a css file
    
.. attribute:: unit

    The unit associated with the value (px, em, %, color or ``nan``)
'''
    def __init__(self, value, unit = None):
        self._value = self.convert(value)
    
    @property
    def value(self):
        return self._value
    
    @property
    def unit(self):
        return self._unit()
    
    def __unicode__(self):
        return force_unicode(self.tocss())
    
    def tojson(self):
        return str(self)
    
    def tocss(self):
        '''Convert this :class:`Variable` to a string suitable for inclusion
in a css file.'''
        return self._value
        
    def __add__(self, other):
        return self._op(other, lambda a,b: a+b)
    
    def __sub__(self, other):
        return self._op(other, lambda a,b: a-b)
    
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __mul__(self, other):
        return self._op(other, lambda a,b: a*b, supported_types = (int,float))
    
    if ispy3k:  # pragma: no cover
        def __truediv__(self, other):
            return div(self,other)
    else:   # pragma: no cover
        def __div__(self, other):
            return div(self,other)        
    
    def __floordiv__(self, other):
        return self._op(other, lambda a,b: a//b, supported_types = (int,float))
    
    def __eq__(self, other):
        if isinstance(other,Variable):
            return self.unit == other.unit and self.value == other.value
        else:
            return False
        
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __lt__(self, other):
        if isinstance(other,Variable):
            if self.unit == other.unit:
                return self.value < self.value
        raise TypeError('Cannot compare "{0}" with "{1}"'.format(self,other))
    
    @classmethod
    def cssvalue(cls, o):
        if isinstance(o, Variable):
            return o.tocss()
        elif isinstance(o, Variables):
            return None
        elif hasattr(o, '__call__'):
            return cls.cssvalue(o())
        else:
            return o
        
    @staticmethod
    def pyvalue(o):
        if isinstance(o, Variable):
            return o.value
        elif isinstance(o, Variables):
            return None
        elif hasattr(o, '__call__'):
            return Variable.pyvalue(o())
        else:
            return o
            
    @classmethod
    def make(cls, val, unit = None):
        if isinstance(val,tuple) and len(val) == 1:
            val = val[0]
        if isinstance(val,(NamedVariable,lazy)):
            val = val.tocss()
        if isinstance(val, cls):
            if not unit or val.unit == unit:
                return val
        elif not isinstance(val, Variable):
            return cls(val, unit = unit)
        return cls._make(val, unit)
    
    @classmethod
    def _make(cls, val, unit):
        raise ValueError('Could not convert "{0}" to "{1}".'\
                        .format(val,cls.__name__))

    ##    INTERNALS
    
    def convert(self, value):
        return value
    
    def _unit(self):
        return nan
    
    def _op(self, other, ope, supported_types = None):
        oval = None
        if not supported_types:
            other = self.make(other, self.unit)
            if other.unit == self.unit:
                oval = other.value
        elif isinstance(other, supported_types):
            oval = other
        if oval is None:
            raise TypeError('Cannot perform operation')
        else:
            return self._do_operation(ope, oval)
        
    def _do_operation(self, ope, oval):
        return self.__class__(ope(self.value, oval), unit = self.unit)
    
    
class ProxyVariable(Variable):

    def __init__(self, value, unit = None):
        self.value = value
        
    def _get_value(self):
        return self._get()
    def _set_value(self, value):
        value = self.convert(value)
        return self._set(value)
    value = property(_get_value,_set_value)
            
    def _unit(self):
        v = self.tocss()
        return v.unit if isinstance(v,Variable) else None
    
    def _get(self):
        value = self.tocss()
        return value.value if isinstance(value,Variable) else value
    
    def _set(self, value):
        self._value = value
        
    def _do_operation(self, ope, oval):
        value = self.tocss()
        return value._do_operation(ope, oval)
    
    
class lazy(ProxyVariable):
    '''A lazy :class:`Variable`.'''
    def __init__(self, callable, *args, **kwargs):
        if not hasattr(callable,'__call__'):
            raise TypeError('First argument must be a callable')
        super(lazy,self).__init__((callable, args, kwargs))
    
    def tocss(self):
        callable, args, kwargs = self._value
        return callable(*args, **kwargs)
    
    
class NamedVariable(ProxyVariable):
    '''A variable holds several values for different styles.
    
.. attribute:: name

    variable name
'''
    def __init__(self, hnd, name, value):
        self.hnd = hnd
        self._name = name
        self._values = {}
        super(NamedVariable, self).__init__(value)
        
    @property
    def name(self):
        return self._name
    
    @property
    def theme(self):
        return self.hnd.theme
    
    def tocss(self):
        return self._values.get(self.theme, self._value)
    
    def convert(self, value):
        if not isinstance(value, NamedVariable):
            c = conversions.get(self.name)
            if c:
                if not isinstance(value,c):
                    value = c.make(value)
        return value
            
    def _set(self, value):
        theme = self.theme
        if not isinstance(value, Variable):
            value = Variable(value)           
        if theme in self._values:
            self._values[theme] = value
        else:
            self._value = value
    
    @classmethod
    def _make(cls, val, unit):
        return val
    
    
class Size(Variable):
      
    def __init__(self, value, unit = None):
        self._fix_unit = unit or 'px'
        super(Size, self).__init__(value)
    
    def tocss(self):
        return '{0}{1}'.format(self._value, self.unit)
    
    def convert(self, value):
        value = native_str(value)
        if isinstance(value,str):
            if value[-2:] == self.unit:
                value = value[:-2]
            elif value[-1:] == self.unit:
                value = value[:-1]
            else:
                ValueError('"{0}" is not a valid space'.format(value))
        value = float(value)
        ivalue = int(value)
        return ivalue if ivalue == value else value
    
    def _unit(self):
        return self._fix_unit


class Spacing(Variable):
    '''Handle css Spacing'''
    def __init__(self, top, *right_bottom_left, **kwargs):
        if isinstance(top,(list,tuple)):
            value = list(top)
        else:
            value = [top]
        value.extend(right_bottom_left)
        super(Spacing, self).__init__(value)
        unit = kwargs.get('unit')
        if unit and unit != self.unit:
            raise ValueError('Spacing "{0}" cannot have unit "{1}".'\
                             .format(self,unit))
        
    def tocss(self):
        return ' '.join((str(b) for b in self.value))
    
    def _unit(self):
        unit = self.top.unit
        for v in self.value[1:]:
            if v.unit != unit:
                return nan
        return unit

    def __iter__(self):
        return iter(self.value)
    
    def __len__(self):
        return len(self.value)
        
    @property
    def top(self):
        return self._value[0]
    
    @property
    def right(self):
        return self._value[1] if len(self._value) > 1 else self.top
    
    @property
    def bottom(self):
        return self._value[2] if len(self._value) > 2 else self.top
    
    @property
    def left(self):
        return self._value[3] if len(self._value) > 3 else self.right
    
    def convert(self, value):
        if not isinstance(value, (list,tuple)):
            value = [value]
        if len(value) > 4 or len(value) < 1:
            raise ValueError('Spacing must have at most 4 elements')
        return list((Size.make(v) for v in value))
    
    @classmethod
    def _make(cls, val, unit):
        if isinstance(val, Size) and not unit:
            return cls(val)
        return super(Spacing,cls)._make(val, unit)
    
    
################################################################################
##    factory functions
px = lambda v: Size.make(v, unit = 'px')  
pc = lambda v: Size.make(v, unit = '%')
em = lambda v: Size.make(v, unit = 'em')
spacing = lambda *vals : Spacing.make(vals)
    
    
    
class mixin(UnicodeMixin):
    '''A css *mixin* is a generator of :class:`css` and other
:class:`mixin` elements. All :class:`mixin` must implement the
callable method.'''
    def __call__(self, elem):
        raise NotImplementedError()
    
    @classmethod
    def cleanup(cls, value, attname, constructor = None):
        if isinstance(value, cls):
            value = getattr(value,attname)
        elif isinstance(value, Variables):
            if value.valid() and constructor:
                value = constructor(**value.params())
            else:
                value = None
        return value
    

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
                   'attribute': '',
                   'bigger': ' > '}
    
    def __init__(self, tag):
        self._tag = tag
        self._children = OrderedDict()
        self._parent = None
        self._attributes = []
        self.mixins = []
        
    def _setup(self, *components, **attributes):
        parent = attributes.pop('parent',None)
        self.parent_relationship = attributes.pop('parent_relationship',
                                                  self.parent_relationship)
        for name,value in iteritems(attributes):
            if not isinstance(value, Variables):
                self[name] = value
        self.parent = parent
        for c in components:
            if isinstance(c, CSS):
                c.parent = self
            elif isinstance(c, mixin):
                # add mixin to the list of mixins
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
        for mchild in chain(itervalues(elem._children),
                            itervalues(elem._body._children)):
            for child in mchild:
                for elem in child:
                    yield elem
    
    def clone(self):
        cls = self.__class__
        q = cls.__new__(cls)
        d = self.__dict__.copy()
        d['_attributes'] = copy(d['_attributes'])
        d['_children'] = OrderedDict()
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
            v = Variable.cssvalue(v)
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
Created by style  {0}
------------------------------------------------------------------
------------------------------------------------------------------ */

'''.format(now)
        stream.write(intro)
        CSS._body.render(stream)
        return stream.getvalue()

# global body
CSS._body = CSS('body')

css = css()
def cssa(*args, **kwargs):
    kwargs['parent_relationship'] = 'attribute'
    return css(*args, **kwargs)
def cssb(*args, **kwargs):
    kwargs['parent_relationship'] = 'bigger'
    return css(*args, **kwargs)
    
    
class theme(object):
    
    def __init__(self, hnd, theme):
        self.__dict__['hnd'] = hnd
        self.__dict__['theme'] = theme
    
    def __repr__(self):
        return self.theme
    
    def __setattr__(self, name, value):
        getattr(self.hnd, name).value = value
        
    
class Variables(UnicodeMixin):
    '''Variables container with namespaces. A variable name is split
using the double underscores separator ``__``::

    v = Variables()
    v.body.height = px(16)
    
If the body namespace is not available is automatically created.
'''
    reserved = (None, '_parent', '_name', '_theme')
    
    def __init__(self, parent = None, name = None):
        self.__dict__['_parent'] = parent
        self.__dict__['_name'] = name
        
    def __unicode__(self):
        if self._name:
            return self._name
        else:
            return 'root'
        
    def valid(self):
        '''``True`` if the :class:`Variables` are part of a root dictionary.'''
        return self._name == 'root' or self._parent
        
    def set_theme(self, theme):
        if self._parent:
            self._parent.set_theme(theme)
        else:
            self.__dict__['_theme'] = theme
            
    def theme(self):
        if self._parent:
            return self._parent.theme()
        else:
            return self.__dict__.get('_theme')
    
    def theme_setter(self, theme_name):
        return theme(self, theme_name)
        
    def declare(self, name, value):
        '''Declare or update a variable with *default* value.'''
        if name not in self.reserved and value is not None:
            if isinstance(value, Variables):
                self.__dict__[name] = value
                return value
            elif isinstance(value,(str,float,int,list,tuple,dict,Variable)):
                v = self.get(name)
                if isinstance(v, NamedVariable):
                    v.value = value
                else:
                    v = NamedVariable(self, name, value)
                    self.__dict__[name] = v                
                return v
    
    def get(self, name):
        if name not in self.__dict__:
            return Variables(self, name)
        else:
            return self.__dict__[name]
                
    def __iter__(self):
        d = self.__dict__
        for name in sorted(d):
            if name not in self.reserved:
                yield d[name]
    
    def tojson(self):
        return OrderedDict(((v._name, v.tojson()) for v in self))
        
    def params(self):
        d = self.__dict__
        r = {}
        for name in d:
            if name not in self.reserved:
                r[name] = d[name]
        return r
                
    def __contains__(self, name):
        return name.lower() in self.__dict__
    
    def __setattr__(self, name, value):
        d = self.declare(name, value)
        if d and self._parent and self._name not in self._parent:
            setattr(self._parent, self._name, self) 
    
    def __getattr__(self, name):
        return self.get(name)


################################################################################
##    GLOBAL VARIABLES
################################################################################
cssv = Variables()        

def csscompress(target):  # pragma: no cover
    os.system('yuicompressor.jar --type css -o {0} {0}'.format(target))

def printf(v):  # pragma: no cover
    print(v)
    
memory_symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
memory_size = dict(((s,1 << (i+1)*10) for i,s in enumerate(memory_symbols)))

def convert_bytes(b):
    '''Convert a number of bytes into a human readable memory usage'''
    if b is None:
        return '#NA'
    for s in reversed(memory_symbols):
        if b >= memory_size[s]:
            value = float(b) / memory_size[s]
            return '%.1f%sB' % (value, s)
    return "%sB" % b

def dump_theme(theme, target, show_variables = False, minify = False,
               verbose = True):
    log = printf if verbose else lambda v: v
    cssv.set_theme(theme)
    if show_variables:
        log('STYLE: {0}'.format(cssv.theme() or 'Default'))
        section = None
        data = cssv.tojson()
        log(json.dumps(data, indent = 4))
    else:
        data = css.render()
        f = open(target,'w')
        f.write(data)
        f.close()
        if minify:
            csscompress(target)
        with open(target) as f:
            b = convert_bytes(len(f.read()))
        log('Saved style on file "{0}". Size {1}.'.format(target,b))
    
    
def add_arguments(argparser = None):
    argparser = argparser or argparse.ArgumentParser('Python CSS generator')
    argparser.add_argument('source',
                           nargs='*',
                           help='Dotted path to source files or directories.')
    argparser.add_argument('-t', '--theme',
                           default=None,
                           help='Theme name')
    argparser.add_argument('-o', '--output',
                           help='File path to store CSS into.',
                           default='style.css')
    argparser.add_argument('-v','--variables',
                           action='store_true',
                           default=False,
                           help='List all variables values')
    argparser.add_argument('-m','--minify',
                           action='store_true',
                           default=False,
                           help='Minify output file')
    return argparser
    
    
def main(argparser = None, verbose = True, argv = None):
    argparser = add_arguments(argparser)
    opts = argparser.parse_args(argv)
    for source in opts.source:
        mod = import_module(source)
    
    dump_theme(opts.theme, opts.output, opts.variables, opts.minify,
               verbose = verbose)    
    