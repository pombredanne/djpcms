from djpcms.utils import slugify, merge_dict
from djpcms.utils.py2py3 import iteritems
from djpcms.template import loader, mark_safe, conditional_escape

from .media import BaseMedia

__all__ = ['flatatt',
           'HtmlWidget']


def attrsiter(attrs):
    for k,v in attrs.items():
        if v:
            if k == 'class':
                v = ' '.join(v)
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
    attributes = {'id':None}
    
    def __init__(self, cn = None, template = None, **kwargs):
        attrs = {}
        self.template = template
        for attr,value in iteritems(self.attributes):
            if attr in kwargs:
                value = kwargs[attr]
            attrs[attr] = value
        self.default_style = kwargs.get('default_style',self.default_style)
        self.__attrs = attrs
        self.__classes = set()
        self.addClass(cn)
        
    def flatatt(self):
        cs = ''
        if self.__classes:
            cs = ' '.join(self.__classes)
        self.__attrs['class'] = cs
        return flatatt(self.__attrs)
        
    @property
    def attrs(self):
        return self.__attrs
    
    def addClasses(self, cn, splitter = ' '):
        cns = cn.split(splitter)
        for cn in cns:
            self.addClass(cn)
        return self
    
    def addClass(self, cn):
        if cn:
            cn = slugify(cn)
        if cn:
            self.__classes.add(cn)
        return self
    
    def hasClass(self, cn):
        return cn in self.__classes
                
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
    
    def render(self):
        if self.inline:
            return mark_safe('<{0}{1}/>'.format(self.tag,self.flatatt()))
        else:
            return mark_safe('<{0}{1}>\n{2}\n</{0}>'.format(self.tag,self.flatatt(),self.inner()))
    
    def inner(self):
        return ''

    
class FormWidget(HtmlWidget):
    '''Form Render'''
    default_template = 'djpcms/uniforms/uniform.html'
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
        
    def inner(self):
        return loader.render_to_string(self.template,cd,
                                       context_instance)
    