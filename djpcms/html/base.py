from py2py3 import iteritems

from djpcms import sites, UnicodeMixin
from djpcms.utils import force_str, slugify, escape
from djpcms.utils.collections import OrderedDict
from djpcms.template import loader
from .media import BaseMedia


__all__ = ['flatatt',
           'HtmlAttrMixin',
           'HtmlWidget']

def attrsiter(attrs):
    for k,v in attrs.items():
        if v:
            yield ' {0}="{1}"'.format(k, escape(v))
                
                
def flatatt(attrs):
    return ''.join(attrsiter(attrs))


class HtmlAttrMixin(object):
    '''A mixin class which exposes jQuery alike API for
handling HTML classes and sttributes'''
    def flatatt(self, **attrs):
        '''Return a string with atributes to add to the tag'''
        cs = ''
        attrs = self.attrs.copy()
        if self.classes:
            cs = ' '.join(self.classes)
            attrs['class'] = cs
        if attrs:
            return flatatt(attrs)
        else:
            return ''
        
    @property
    def attrs(self):
        if not hasattr(self,'_HtmlAttrMixin__attrs'):
            self.__attrs = {}
        return self.__attrs
    
    @property
    def classes(self):
        if not hasattr(self,'_HtmlAttrMixin__classes'):
            self.__classes = set()
        return self.__classes
    
    def addClass(self, cn):
        if cn:
            add = self.classes.add
            for cn in cn.split():
                cn = slugify(cn)
                add(cn)
        return self
    
    def addAttr(self, name, val):
        self.attrs[name] = val
        return self
    
    def hasClass(self, cn):
        return cn in self.classes
                
    def removeClass(self, cn):
        '''Remove classes
        '''
        if cn:
            ks = self.classes
            for cn in cn.split():
                if cn in ks:
                    ks.remove(cn)
        return self


class HtmlWidget(BaseMedia,HtmlAttrMixin):
    '''Base class for HTML components. Anything which is rendered as HTML
is derived from this class. Any Operation on this class is similar to jQuery.'''
    tag = None
    is_hidden = False
    default_style = None
    inline = False
    template = None
    attributes = {'id':None}
    default_class = None
    
    def __init__(self, tag = None, cn = None, template = None, js = None,
                 renderer = None, css = None, **kwargs):
        attrs = self.attrs
        self.renderer = renderer
        self.tag = tag or self.tag
        self.template = template or self.template
        for attr,value in iteritems(self.attributes):
            if attr in kwargs:
                value = kwargs.pop(attr)
            attrp = 'process_{0}'.format(attr)
            if hasattr(self,attrp):
                value = getattr(self,attrp)(value)
            if value is not None:
                attrs[attr] = value
        if kwargs:
            keys = list(kwargs.keys())
            raise TypeError("__init__() got an unexpected keyword argument '{0}'".format(keys[0]))
        self.default_style = kwargs.get('default_style',self.default_style)
        if self.default_class:
            self.addClass(self.default_class)
        self.addClass(cn)
        media = self.media
        media.add_js(js)
        media.add_css(css)
    
    def ischeckbox(self):
        return False
        
    def render(self, *args, **kwargs):
        fattr = self.flatatt()
        html = self._render(fattr, *args, **kwargs)
        if self.renderer:
            return self.renderer(html)
        else:
            return html
    
    def _render(self, fattr, *args, **kwargs):
        if self.inline:
            return '<{0}{1}/>'.format(self.tag,fattr)
        elif self.tag:
            return '<{0}{1}>\n{2}\n</{0}>'.format(self.tag,fattr,
                                                  self.inner(*args, **kwargs))
        else:
            return self.inner(*args, **kwargs)
    
    def get_context(self, context, *args, **kwargs):
        pass
    
    def inner(self, *args, **kwargs):
        '''Render the inner template'''
        if self.template:
            context = {}
            self.get_context(context,*args,**kwargs)
            return loader.render(self.template,context)
        else:
            return ''


class htmlbase(object):
    
    def get_template(self):
        template = getattr(self,'template',None)
        if template:
            return template
        else:
            raise NotImplementedError
    
    def __repr__(self):
        return self.render()
    __str__ = __repr__
    
    def get_content(self):
        return {'html': self,
                'css':  sites.settings.HTML_CLASSES}
    
    def getplugins(self, ftype):
        return None
    
    def items(self):
        return []
    
    def attrs(self):
        return None
    
    def addClass(self, cn):
        return self
    
    def hasClass(self, cn):
        return False
                
    def removeClass(self, cn):
        return self
    
    def flatatt(self):
        attrs = self.attrs()
        return '' if not attrs else flatatt(attrs)
        
    def render(self):
        return loader.render_to_string(self.get_template(),
                                       self.get_content())
        
        
class htmlattr(htmlbase):
    '''
    HTML utility with attributes a la jQuery
    '''
    def __init__(self, cn = None, **attrs):
        self._attrs = attrs
        self.addClass(cn)
    
    def attrs(self):
        return self._attrs
    
    def addClasses(self, cn):
        cns = cn.split(' ')
        for cn in cns:
            self.addClass(cn)
        return self
    
    def addClass(self, cn):
        if cn:
            cn = str(cn).replace(' ','')
        if cn:
            attrs = self._attrs
            c    = attrs.get('class',None)
            if c:
                cs = c.split(' ')
                if cn not in cs:
                    attrs['class'] = '%s %s' % (c,cn)
            else:
                attrs['class'] = cn
        return self
    
    def hasClass(self, cn):
        css = self._attrs['class'].split(' ')
        return cn in css
                
    def removeClass(self, cn):
        '''
        remove a class name from attributes
        '''
        css = self._attrs['class'].split(' ')
        for i in range(0,len(css)):
            if css[i] == cn:
                css.pop(i)
                break
        self._attrs['class'] = ' '.join(css)
        return self
    

class htmltag(htmlattr):
    
    def __init__(self, tag, **attrs):
        self.tag = tag
        super(htmltag,self).__init__(**attrs)


class htmltiny(htmltag):
    
    def __init__(self, tag, **attrs):
        super(htmltiny,self).__init__(tag, **attrs)
    
    def render(self):
        return '<{0}{1}/>'.format(self.tag,self.flatatt())
    
    
class htmlwrap(htmltag):
    '''
    wrap a string within a tag
    '''
    def __init__(self, tag, inner, **attrs):
        self.inner = inner
        super(htmlwrap,self).__init__(tag, **attrs)
    
    def render(self):
        return mark_safe('\n'.join(['<%s%s>' % (self.tag,self.flatatt()),
                                     self.inner,
                                     '</%s>' % self.tag]))
    
    
class htmlcomp(htmltag):
    '''
    HTML component with inner components
    '''
    def __init__(self, tag, template = None, inner = None, **attrs):
        super(htmlcomp,self).__init__(tag, **attrs)
        self.template = template
        self.tag      = tag
        self.inner    = OrderedDict()
        if inner:
            self['inner'] = inner
        
    def __setitem__(self, key, value):
        if isinstance(value, htmlbase):
            self.inner[key] = value
        
    def items(self):
        for v in self.inner.values():
            yield v
    
    def _get_media(self):
        """
        Provide a description of all media required to render the widgets on this form
        """
        media = Media()
        items = self.items()
        for item in items:
            m = getattr(item,'media',None)
            if m:
                media = media + m
        return media
    media = property(_get_media)
    
    def getplugins(self, ftype):
        '''
        Return a list of plugings of type ftype
        '''
        fs = []
        for c in self.inner.values():
            if isinstance(c,ftype):
                fs.append(c)
            elif isinstance(c,htmlcomp):
                fs.extend(c.getplugins(ftype))
        return fs
    
    def get_template(self):
        if self.template:
            return self.template
        top = 'components/%s.html' % self.tag
        return [top,
                'djpcms/%s' % top,
                'components/htmlcomp.html',
                'djpcms/components/htmlcomp.html']
        
    
class input(htmltiny):
    
    def __init__(self, name = 'submit', value = 'submit', type = 'submit', **attrs):
        super(input,self).__init__('input', name = name, value = value,
                                    type = type, **attrs)

