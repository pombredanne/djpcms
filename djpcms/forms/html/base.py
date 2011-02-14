from py2py3 import iteritems

from djpcms.utils import slugify, merge_dict
from djpcms.template import loader, mark_safe, conditional_escape

from .media import BaseMedia

__all__ = ['flatatt',
           'HtmlWidget']


def attrsiter(attrs):
    for k,v in attrs.items():
        if v:
            yield ' {0}="{1}"'.format(k, conditional_escape(v))
                
                
def flatatt(attrs):
    return ''.join(attrsiter(attrs))


class HtmlWidget(BaseMedia):
    '''Base class for HTML components. Anything which is rendered as HTML
is derived from this class. Any Operation on this class is similar to jQuery.'''
    tag = None
    is_hidden = False
    default_style = None
    inline = False
    template = None
    attributes = {'id':None}
    
    def __init__(self, tag = None, cn = None, template = None, **kwargs):
        attrs = {}
        self.tag = tag or self.tag
        self.template = template or self.template
        for attr,value in iteritems(self.attributes):
            if attr in kwargs:
                value = kwargs.pop(attr)
            attrs[attr] = value
        if kwargs:
            keys = list(kwargs.keys())
            raise TypeError("__init__() got an unexpected keyword argument '{0}'".format(keys[0]))
        self.default_style = kwargs.get('default_style',self.default_style)
        self.__attrs = attrs
        self.__classes = set()
        self.addClass(cn)
        
    def flatatt(self, **attrs):
        '''Return a string with atributes to add to the tag'''
        cs = ''
        if self.__classes:
            cs = ' '.join(self.__classes)
        self.__attrs['class'] = cs
        if attrs:
            _attrs = self.__attrs.copy()
            _attrs.update(attrs)
            return flatatt(_attrs)
        else:
            return flatatt(self.__attrs)
    
    def ischeckbox(self):
        return False
        
    @property
    def attrs(self):
        return self.__attrs
    
    @property
    def classes(self):
        return self.__classes
    
    def addClass(self, cn):
        if cn:
            add = self.__classes.add
            for cn in cn.split():
                cn = slugify(cn)
                add(cn)
        return self
    
    def hasClass(self, cn):
        return cn in self.__classes
                
    def removeClass(self, cn):
        '''remove a class name from attributes
        '''
        if cn:
            ks = self.__classes
            for cn in cn.split():
                if cn in ks:
                    ks.remove(cn)
        return self
    
    def render(self, *args, **kwargs):
        fattr = self.flatatt()
        return self._render(fattr, *args, **kwargs)
    
    def render_from_field(self, djp, field):
        fattr = self.flatatt(name = field.html_name, id = field.id, value = field.value)
        return self._render(fattr, djp, field)
    
    def _render(self, fattr, *args, **kwargs):
        if self.inline:
            return mark_safe('<{0}{1}/>'.format(self.tag,fattr))
        elif self.tag:
            return mark_safe('<{0}{1}>\n{2}\n</{0}>'.format(self.tag,fattr,
                                                            self.inner(*args, **kwargs)))
        else:
            return self.inner(*args, **kwargs)
    
    def inner(self, *args, **kwargs):
        return ''

    
class FormWidget(HtmlWidget):
    '''Form HTML widget'''
    tag = 'form'
    attributes = merge_dict(HtmlWidget.attributes, {
                                                    'method':'post',
                                                    'enctype':'multipart/form-data',
                                                    'action': '.'
                                                    })
    def __init__(self, form, layout, inputs = None, **kwargs):
        super(FormWidget,self).__init__(**kwargs)
        self.form = form
        self.layout = layout
        self.inputs = inputs
        self.addClass(self.layout.form_class)
        
    def inner(self, djp = None):
        return self.layout.render(djp,
                                  self.form,
                                  self.inputs)
        
    def is_valid(self):
        '''Proxy for self.forms.is_valid'''
        return self.form.is_valid()
    
    def add(self, elem):
        '''Add extra element to the form widget'''
        pass
    