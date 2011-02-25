from copy import copy

from djpcms import template, nodata
from djpcms.utils.collections import OrderedDict


from .defaults import body_defaults, jqueryui


_root = None
_context_dictionary = OrderedDict()


class _CssContext(object):
    template = 'medplate/elem.css_t'
    
    def __init__(self, name, tag = None, template = None,
                 description = '', elems= None,
                 data = None, ineritable_tag = True,
                 defaults = None, process = None,
                 parent = None, same_as_parent = False):
        global _root, _context_dictionary
        self.parent = None
        self.themes = {}
        self._tag = tag or ''
        self.same_as_parent = same_as_parent
        self.process = process
        self._ineritable_tag = ineritable_tag
        self.template = template or self.template
        self.description = description
        self.data = data or {}
        self.defaults = defaults or {}
        if not name:
            if _root:
                raise KeyError('Body css template already defined')
            _root = self
            self.context_dictionary = _context_dictionary
        else:
            name = name.lower()
            self.context_dictionary = OrderedDict()
            self.name = name
            cd = _context_dictionary
            if parent:
                if not isinstance(parent,self.__class__):
                    if parent not in _context_dictionary:
                        raise KeyError('Parent {0} not available'.format(parent))
                    else:
                        parent = _context_dictionary[parent]
                cd = parent.context_dictionary
                self.parent = parent
            if name in cd:
                raise KeyError('Css context {0} already available'.format(name))
            cd[name] = self
        if elems:
            for elem in elems:
                self.add(elem)
        
    def __str__(self):
        return self.tag()

    def __repr__(self):
        return self.__str__()
    
    def tag(self):
        tag = ''
        if self.parent:
            tag = self.parent.ineritable_tag()
            if tag and not self.same_as_parent:
                tag += ' '
        return tag + self._tag
    
    def ineritable_tag(self):
        if self._ineritable_tag:
            return self.tag()
        else:
            return ''
    
    def render(self, style, media_url, template_engine = None):
        '''Render the css context'''
        loader = template.handle(template_engine)
        tag = self.tag()
        data = self.defaults.copy()
        data.update(self.data)
        if self.process:
            data = self.process(data)
        data['MEDIA_URL'] = media_url
        data['tag'] = tag
        data['description'] = self.description or tag
        data['elems'] = (elem.render(style,media_url,template_engine) for\
                            elem in self.context_dictionary.values())
        self.extra_data(loader,data,style)
        if style in self.themes:
            sdata = self.themes[style].data
            data.update(sdata)
        return loader.render(self.template,data)
    
    def extra_data(self, loader, data, style):
        pass
    
    def update(self, data):
        self.data.update(data)
    
    def add(self, value):
        if isinstance(value,_CssContext):
            self.context_dictionary[value.name] = value
            
    def __iter__(self):
        return iter(self.data)
    
    def get(self, key, default = None):
        try:
            return getattr(self,key)
        except AttributeError:
            return default
        
    def __getattr__(self, key):
        v = self.data.get(key, nodata)
        if v is nodata:
            if self.parent:
                try:
                    v = getattr(self.parent,key)
                except AttributeError:
                    pass
                
            if v is nodata:
                v = self.defaults.get(key, nodata)
                if v is nodata:
                    raise AttributeError('No attribute {0} avaialble'.format(key))
        
        return v
        
    def __contains__(self, key):
        try:
            self[key]
            return True
        except KeyError:
            return False
    
    def __getitem__(self, key):
        try:
            item = getattr(self,key)
            if hasattr(item,'__call__'):
                item = item()
            return item
        except AttributeError:
            raise KeyError
        
    def copy(self, data = None):
        d = self.__dict__.copy()
        d.pop('elems')
        d['parent'] = None
        if data:
            d['data'] = data
        obj = self.__new__(self.__class__)
        obj.__dict__ = d
        obj.elems = []
        for elem in self.elems:
            obj.add(elem.copy())
        return obj
           
           
class CssBody(_CssContext):
    template = 'medplate/body.css_t'
    
    def __init__(self, data = None):
        super(CssBody,self).__init__(None,'body',
                                     ineritable_tag = False,
                                     defaults = body_defaults,
                                     data = data)
        
    def extra_data(self, loader, data, style):
        data['jquery'] = jqueryui(data,loader,style)
        

class DummyBody(_CssContext):
    template = 'medplate/root.css_t'
    
    def __init__(self, data = None):
        super(DummyBody,self).__init__(None,None,
                                      ineritable_tag = False,
                                      data = data)
        
        
class _CssTheme(object):
    '''Add theme to Context'''    
    def __init__(self, context, name, data):
        context.themes[name] = self
        self.context = context
        self.name = name
        self.data = data
    
    def __str__(self):
        return '{0}.{1}'.format(self.context,self.name)



def get_context(name):
    cts = name.split()
    context = _context_dictionary[cts[0]]
    for c in cts[1:]:
        context = context.context_dictionary[c]
    return context


def CssContext(name, parent = None, **kwargs):
    cts = name.split()
    cd = _context_dictionary
    parent = parent
    context = None
    for name in tuple(cts):
        if name in cd:
            parent = context
            context = cd[name]
            cd = context.context_dictionary
            cts.pop(0)
        else:
            context = None
            break
    if context and not cts:
        return context
    
    if len(cts) > 1:
            raise ValueError
    return _CssContext(cts[0], parent = parent, **kwargs)
    

def CssTheme(context, name, data = None):
    if not isinstance(context,_CssContext):
        context = get_context(context)
    if not data:
        data = {}
    if name in context.themes:
        theme = context.themes[name]
        theme.data.update(data)
    else:
        _CssTheme(context,name,data)
 
    
def rendercss(style, media_url, template_engine = None):
    '''Entry point for rendering css templates.
    '''
    root = _root
    if not root:
        root = DummyBody() 
    return root.render(style, media_url, template_engine)
    
    
         
         
        