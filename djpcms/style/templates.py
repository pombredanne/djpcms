from djpcms.utils.py2py3 import UnicodeMixin
from djpcms.html import WidgetMaket

__all__ = ['css', 'var']

def deval(o):
    return o.value if isinstance(o,Variable) else o


class cssgenerator(UnicodeMixin):
    name = 'cssgenerator'
    def __call__(self):
        raise NotImplementedError


class css(UnicodeMixin):
    
    def __init__(self, tag, *children, **attributes):
        self._tag = tag
        self.children = children
        self.parent = attributes.pop('parent',None)
        self.process = attributes.pop('process',None)
        self.attributes = dict(((k.replace('_','-'),v)\
                                 for k,v in iteritems(attributes)))
        
    @property
    def tag(self):
        if self.parent:
            return self.parent.tag + ' ' + self._tag
        else:
            return self._tag
    
    def stream(self):
        yield self.tag + ' {'
        for k,v in iteritems(self.attributes):
            yield '    {0}: {1};'.format(k,v)
        yield '}'
        
    def __unicode__(self):
        return '\n'.join(self.stream())
    

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
        return self.hnd.theme
    
    @property
    def value(self):
        return self.values.get(self.theme,self.default_value)
    
    def __unicode__(self):
        value = self.value
        if isinstance(value,cssgenerator):
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
    
    
class ThemeSetter(object):
    
    def __init__(self, hnd, theme):
        self.__dict__['hnd'] = hnd
        self.__dict__['theme'] = theme
    
    def __setattr__(self, name, value):
        getattr(self.hnd,name).values[self.theme] = value
        
    
class Variables(object):
    
    def __init__(self):
        self.__dict__['theme'] = None
        
    def set_theme(self, theme):
        self.__dict__['theme'] = theme
        
    def theme_setter(self, theme):
        return ThemeSetter(self,theme)
        
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
            self.__dict__[name] = Variable(self,name,value)
            
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
        
    def declare_from_module(self, mod):
        for name in dir(mod):
            if name.startswith('_'):
                continue
            if name == name.lower():
                val = getattr(mod,name)
                self.set_or_declare(name,val)

        
vars = Variables()
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