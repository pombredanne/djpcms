from copy import copy

from djpcms import template, sites, nodata


class CssContext(object):
    template = 'medplate/elem.css_t'
    
    def __init__(self, name, tag = None, template = None,
                 description = '', elems= None,
                 data = None, ineritable_tag = True,
                 defaults = None, process = None):
        self.mediaurl = sites.settings.MEDIA_URL
        self.name = name
        self._tag = tag
        self.process = process
        self._ineritable_tag = ineritable_tag
        self.template = template or self.template
        self.parent = None
        self.description = description or self._tag
        self.data = data or {}
        self.defaults = defaults or {}
        self.elems = []
        self.jquery_ui_theme = 'smooth'
        elems = elems or []
        for elem in elems:
            self.add(elem)
        
    def __str__(self):
        return self.render()

    def __repr__(self):
        return self.__str__()
    
    def tag(self):
        tag = ''
        if self.parent:
            tag = self.parent.ineritable_tag()
            if tag:
                tag += ' '
        return tag + self._tag
    
    def ineritable_tag(self):
        if self._ineritable_tag:
            return self.tag()
        else:
            return ''
    
    def render(self, template_engine = None):
        loader = template.handle(template_engine)
        if self.process:
            data = self.copy(self.process(self.data))
        else:
            data = self
        data.data['jquery'] = self.jqueryui(loader)
        return loader.render(self.template,data)
    
    def update(self, data):
        self.data.update(data)
    
    def add(self, value):
        '''Add a csscontext to self.
        When adding, ``value`` is appended to the elems
        list attribute of ``self`` and the ``parent`` attribute of
        ``value`` is set to ``self``. In addition ``value`` is added
        to the ``data`` dictionary attribute of ``self``.'''
        if isinstance(value,CssContext):
            self.elems.append(value)
            value.parent = self
            self.data[value.name] = value
            
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
    
    def jqueryui(self, loader):
        if self.jquery_ui_theme:
            base  = 'jquery-ui-css/{0}/'.format(self.jquery_ui_theme)
            data = loader.render(base + 'jquery-ui.css')
            toreplace = 'url(images'
            replace = 'url({0}djpcms/'.format(self.mediaurl) + base + 'images'
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
        else:
            return ''
            