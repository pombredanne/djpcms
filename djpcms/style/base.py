'''A python CSS framework'''
import sys
import os
import argparse
import json
import threading
import logging
from copy import copy
from datetime import datetime
from inspect import isgenerator

from djpcms.utils.structures import OrderedDict
from djpcms.utils.text import UnicodeMixin
from djpcms.utils.httpurl import StringIO, itervalues, iteritems,\
                                 native_str, to_string, ispy3k

__all__ = ['css', 'cssa', 'cssb', 'css_stream',
           'Variable', 'NamedVariable', 'mixin',
           'cssv', 'lazy', 'px', 'em', 'pc',
           'spacing', 'dump_theme', 'main', 'Variables',
           'add_arguments']

LOGGER = logging.getLogger('djpcms.style')
nan = float('nan')
conversions = {}

def clamp(val, maxval = 1):
    return min(maxval, max(0, val))

def div(self,other):
    return self._op(other, lambda a,b: a/float(b),
                    supported_types = (int,float))
    
def alltags(tags):
    '''Generator of all tags from a string.'''
    tags = tags.split(',')
    for tag in tags:
        # we trim front spaces
        while tag and tag.startswith(' '):
            tag = tag[1:]
        if tag:
            yield tag
    
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
        return to_string(self.tocss())
    
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
        if isinstance(val,(NamedVariable, lazy)):
            val = val.tocss()
        if isinstance(val, cls):
            if not unit or val.unit == unit:
                return val
        elif not isinstance(val, Variable):
            return cls(val, unit = unit)
        return cls._make(val, unit)
    
    @classmethod
    def _make(cls, val, unit):
        return val

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
    
.. attribute:: theme

    current theme
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
        value = round(value,4)
        ivalue = int(value)
        if self.unit == 'px':
            return ivalue
        else:
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
    
    def __unicode__(self):
        return to_string(self.__class__.__name__)
    
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
        

class css(object):
    '''A :class:`css` element in python.'''
    # pointer to the global css body. The root of all css elements
    lock = threading.Lock()
    rendered = False
    parent_link = {'child': ' ',
                   'attribute': '',
                   'bigger': ' > '}
    
    def __new__(cls, tag, *components, **attributes):
        if tag == 'body':
            elems = [cls.body()]
        elif tag:
            elems = [cls.make(tag) for tag in alltags(tag)]
        else:
            elems = [cls.make(tag)]
        parent = attributes.pop('parent',None)
        parent_relationship = attributes.pop('parent_relationship','child')
        for self in elems:
            self.parent_relationship = parent_relationship
            for name, value in iteritems(attributes):
                self[name] = value
            self._set_parent(parent)
            # Loop over components to add them to self
            for cl in components:
                if not isinstance(cl, list):
                    cl = (cl,)
                for c in cl: 
                    self.add(c)
        return elems[0] if len(elems) == 1 else elems
    
    def __repr__(self):
        return self.tag
    __str__ = __repr__
    
    def __setitem__(self, name, value):
        if value is None or isinstance(value, Variables):
            return
        if isinstance(value, mixin):
            raise TypeError('Cannot assign a mixin to {0}. Use add instead.'\
                            .format(name))
        name = name.replace('_','-')
        self._attributes.append((name,value))
    
    def __getitem__(self, name):
        raise NotImplementedError('cannot get item')
    
    def add(self, c):
        '''Add a child :class:`css` or a class:`mixin`.'''
        if isinstance(c, css):
            c._set_parent(self)
        elif isinstance(c, mixin):
            if self._clone:
                c(self)
            else:
                self._children[str(c)] = c
        else:
            raise TypeError('"{0}" is not a valid type'.format(c))
        
    def clone(self):
        if self._clone:
            return self
        elem = self.make(self._tag, clone = True)
        elem.parent_relationship = self.parent_relationship
        elem._attributes.extend(self._attributes)
        # first unwind mixins
        children = elem._children
        for tag, child in iteritems(self._children):
            if isinstance(child, mixin):
                child(elem)
            elif tag in children:
                children[tag].extend(child)
            else:
                children[tag] = list(child)
        
        # now aggregate
        children = elem._children
        elem._children = OrderedDict()
        for tag, child_list in iteritems(children):
            for child in child_list:
                child = child.clone()
                child._set_parent(elem)
        elem.restore(elem)
        return elem
        
    @property
    def tag(self):
        return self._full_tag(self._tag)
    
    @property
    def code(self):
        return self._tag
    
    @property
    def parent(self):
        return self._parent
    
    @property
    def is_body(self):
        return self._tag == 'body'
    
    def remove(self, child):
        '''Safely remove child *elem* form :class:`css`'''
        if isinstance(child, css):
            code = child.code
            c = self._children.get(code)
            if c:
                try:
                    c.remove(child)
                except ValueError:
                    pass
                if not c:
                    self._children.pop(code)
        elif isinstance(child, mixin):
            self._children.pop(str(child),None)
                
    def extend(self, elem):
        '''Extend by adding *elem* attributes and children.'''
        self._attributes.extend(elem._attributes)
        for child_list in itervalues(elem._children):
            for child in tuple(child_list): 
                child._set_parent(self) 
    
    def stream(self):
        '''This function convert the :class:`css` element into a string.'''
        self.lock.acquire()
        try:
            elem = self.clone()
            for s in elem._stream():
                yield s
        finally:
            self.lock.release()
    
    def render(self):
        '''Render the :class:`css` component and all its children'''
        return '\n'.join(self.stream())
    
    ############################################################################
    ##    PRIVATE METHODS
    ############################################################################
    
    def _full_tag(self, tag):
        if self._parent and self._parent.tag != 'body':
            c = self.parent_link[self.parent_relationship]
            return self._parent.tag + c + tag
        else:
            return tag
        
    def _set_parent(self, parent):
        # Get the element if available
        if self.tag == 'body':
            if parent:
                raise ValueError('Body cannot have parent')
            return self
        # When switching parents, remove itself from current parent children
        if self._parent:
            self._parent.remove(self)
        clone = self._clone
        self._parent = parent = parent or self.body()
        self._clone = parent._clone
        # If the parent is a clone, unwind mixins        
        if not clone and self._clone and self._children:
            children = self._children
            self._children = OrderedDict()
            for tag, c in iteritems(children):
                if isinstance(c, mixin):
                    c(self)
                else:
                    self._children[tag] = c
        c = parent._children.get(self.code)
        if isinstance(c, list) and self not in c:
            c.append(self)
        else:
            parent._children[self.code] = [self]
                
    def _stream(self):
        if self.rendered:
            raise StopIteration()
        self.rendered = True
        data = []
        for k,v in self._attributes:
            v = Variable.cssvalue(v)
            if v is not None:
                data.append('    {0}: {1};'.format(k,v))
        if data:
            # yield the element
            yield self.tag + ' {'
            for s in data:
                yield s
            yield '}\n'
        # yield mixins and children
        for child_list in itervalues(self._children):
            child = child_list[0]
            for c in child_list[1:]:
                child.extend(c)
            for s in child._stream():
                yield s
    
    ############################################################################
    ##    CLASS METHODS
    ############################################################################
    
    @classmethod
    def local(cls):
        thread = threading.current_thread()
        data = getattr(thread, '_css_local', None)
        if data is None:
            data = threading.local()
            thread._css_local = data
            bd = cls.make('body')
            data.real_body = None
            data.body = bd
        return thread._css_local
    
    @classmethod
    def body(cls):
        return cls.local().body
    
    @classmethod
    def make(cls, tag, clone = False):
        o = super(css,cls).__new__(cls)
        if tag == 'body' and clone:
            data = cls.local()
            data.real_body = data.body
            data.body = o
        o._tag = tag
        o._children = OrderedDict()
        o._attributes = []
        o._parent = None
        o._clone = clone
        return o
    
    @classmethod
    def restore(cls, elem):
        if elem.tag == 'body':
            data = cls.local()
            bd = data.real_body
            data.body, data.real_body = bd, None

    @classmethod
    def get(cls, tag):
        return cls.body()._children.get(tag)
        
    @classmethod
    def render_all(cls, media_url = None, charset = 'utf-8'):
        if media_url:
            cssv.MEDIAURL = media_url
        now = datetime.now()
        body = cls.body().render()
        dt = datetime.now() - now
        nice_dt = round(dt.seconds+0.000001*dt.microseconds,3)
        intro = '''\
/*
------------------------------------------------------------------
------------------------------------------------------------------
Theme "{0}"
Created by djpcms.style {1}
Time taken {2} seconds
------------------------------------------------------------------
------------------------------------------------------------------ */

'''.format(cssv.theme(), now, nice_dt)
        return intro + body

def cssa(*args, **kwargs):
    kwargs['parent_relationship'] = 'attribute'
    return css(*args, **kwargs)

def cssb(*args, **kwargs):
    kwargs['parent_relationship'] = 'bigger'
    return css(*args, **kwargs)
    
    
class css_stream(css):

    def __new__(cls, code, stream):
        o = super(css_stream,cls).__new__(cls, code)
        o._data = stream
        return o
    
    @property
    def tag(self):
        return ''
    
    def _stream(self):
        yield self._data
            
        
class theme(object):
    
    def __init__(self, hnd, theme):
        self.__dict__['hnd'] = hnd
        self.__dict__['theme'] = theme
    
    def __repr__(self):
        return self.theme
    __str__ = __repr__
    
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
        if name not in self.reserved:
            if value is None:
                v = NamedVariable(self, name, value)
                self.__dict__[name] = v             
                return v
            elif isinstance(value, Variables):
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
cssv.MEDIAURL = '/media/'

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

def dump_theme(theme, target, show_variables = False, minify = False):
    cssv.set_theme(theme)
    if show_variables:
        LOGGER.info('STYLE: {0}'.format(cssv.theme() or 'Default'))
        section = None
        data = cssv.tojson()
        LOGGER.info(json.dumps(data, indent = 4))
    else:
        data = css.render_all()
        f = open(target,'w')
        f.write(data)
        f.close()
        if minify:
            csscompress(target)
        with open(target) as f:
            b = convert_bytes(len(f.read()))
        LOGGER.info('Saved style on file "{0}". Size {1}.'.format(target,b))
    
    
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
    
    
def main(argparser = None, argv = None):
    argparser = add_arguments(argparser)
    opts = argparser.parse_args(argv)
    for source in opts.source:
        mod = import_module(source)
    
    dump_theme(opts.theme, opts.output, opts.variables, opts.minify)    
    