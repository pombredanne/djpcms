'''Script for writing css files in a pythonic way.
Not templating, just python functions and magic.

The main classes here are :class:`css` and :class:`mixin`.
'''
from datetime import datetime
from inspect import isgenerator

from djpcms.utils.py2py3 import UnicodeMixin, iteritems, itervalues, StringIO,\
                                native_str
from djpcms.utils.structures import OrderedDict

__all__ = ['css', 'var', 'mixin', 'cssv', 'as_mixin', 'deval']


def deval(o):
    return o.value if isinstance(o,var) else o

def itertuple(mapping):
    if isinstance(mapping,dict):
        return iteritems(mapping)
    else:
        return mapping
    
def unwind(components):
    '''Unwind components into individual css elements'''
    for c in components:
        if isinstance(c, css):
            yield c
        elif isinstance(c, mixin):
            for m in unwind(c()):
                yield m                    

def as_mixin(value):
    if isinstance(value,mixin):
        return value
    elif isinstance(value,css):
        return unary_mixin(value)
    else:
        raise valueError('Unsupported value "{0}".'.format(value))
    
    
class mixin(UnicodeMixin):
    '''A css *mixin* is a generator of :class:`css` and other
:class:`mixin` elements. All :class:`mixin` must implement the
callable method.'''
    def __call__(self):
        raise NotImplementedError()
    
    def css(self):
        return list(unwind(self()))
    
    
class unary_mixin(mixin):
    
    def __init__(self, elem):
        self.elem = elem
        
    def __call__(self):
        yield self.elem
    
    
class css(UnicodeMixin):
    _elements = OrderedDict()
    _temp = {}
    def __init__(self, tag, *components, **attributes):
        self._tag = tag
        self._parent = None
        parent = attributes.pop('parent',None)
        self.process = attributes.pop('process',None)
        self._attributes = list(itertuple(attributes.pop('data',{})))
        for name,value in iteritems(attributes):
            self[name] = value
        self.parent = parent
        self.set_components(components)
        
    def set_components(self, components):
        for c in unwind(components):
            c.parent = self                    
    
    def __setitem__(self, name, value):
        if value is not None:
            name = name.replace('_','-')
            self._attributes.append((name,value))
    
    def __getitem__(self, name):
        raise NotImplementedError()
    
    def __len__(self):
        return len(self._attributes)
    
    def __iter__(self):
        return iter(self._attributes)
    
    @property
    def tag(self):
        return self._full_tag(self._tag)

    def _full_tag(self, tag):
        if self._parent:
            return self._parent.tag + ' ' + tag
        else:
            return tag
            
    def _get_parent(self):
        return self._parent
    def _set_parent(self, parent):
        q = self._temp.get(self.tag)
        if q:
            for i,c in enumerate(list(q)):
                if c is self:
                    q.pop(i)
        if parent:
            if self.tag == 'body':
                raise ValueError('Body cannot have parent')
            if self._elements.get(self.tag) == self:
                self._elements.pop(self.tag)
        self._parent = parent
        if self.tag not in self._elements:
            self._elements[self.tag] = self
        else:
            q = self._temp.get(self.tag)
            if q is None:
                q = []
                self._temp[self.tag] = q
            q.append(self)
    parent = property(_get_parent,_set_parent)
    
    def alltags(self):
        tags = self._tag.split(',')
        for tag in tags:
            if tag:
                yield self._full_tag(tag)
                
    def stream(self):
        tag = ',\n'.join(self.alltags())
        yield tag + ' {'
        for k,v in self:
            yield '    {0}: {1};'.format(k,v)
        yield '}'
        
    def __unicode__(self):
        return '\n'.join(self.stream())
    
    @classmethod
    def get(cls, tag):
        return cls._elements.get(tag)
    
    @classmethod
    def render(cls, media_url, charset = 'utf-8'):
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
        elems = cls._elements.copy()
        for k,q in iteritems(cls._temp):
            # the last one overrides all the others
            if q:
                elems[k] = q[-1]
        for elem in itervalues(elems):
            stream.write(elem.__unicode__())
            stream.write('\n\n')
        return stream.getvalue()
    

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
        getattr(self.hnd,name).values[self.theme] = value
        
    
class Variables(object):
    
    def set_theme(self, theme):
        self.__dict__['_theme'] = theme
        
    def theme(self):
        return self.__dict__.get('_theme')
    
    def theme_setter(self, theme):
        return theme(self, theme)
        
    def declare(self, name, default):
        name = name.lower()
        if name in self.__dict__:
            raise KeyError('variable {0} already declared'.format(name))
        self.__dict__[name] = Variable(self,name,default)
    
    def __iter__(self):
        d = self.__dict__
        for name in sorted(d):
            val = d[name]
            if isinstance(val,Variable):
                yield val
                
    def set_or_declare(self, name, value):
        if not name:
            return
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
                val = getattr(module,name)
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

