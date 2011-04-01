import json

from py2py3 import iteritems

from djpcms import sites, UnicodeMixin, is_string
from djpcms.utils import force_str, slugify, escape, mark_safe
from djpcms.utils.collections import OrderedDict
from djpcms.utils.const import NOTHING
from djpcms.template import loader
from .media import BaseMedia


__all__ = ['flatatt',
           'HtmlAttrMixin',
           'HtmlWidget']


def attrsiter(attrs):
    for k,v in attrs.items():
        if v not in NOTHING:
            yield " {0}='{1}'".format(k, escape(v))

                
def flatatt(attrs):
    return ''.join(attrsiter(attrs))


def dump_data_value(v):
    if not is_string(v):
        if isinstance(v,bytes):
            v = v.decode()
        else:
            v = json.dumps(v)
    return mark_safe(v)

class HtmlAttrMixin(object):
    '''A mixin class which exposes jQuery-alike API for
handling HTML classes, attributes and data::

    >>> a = HtmlAttrMixin().addClass('bla foo').addAttr('name','pippo')
    >>> a.classes
    {'foo', 'bla'}
    >>> a.attrs
    {'name': 'pippo'}
    >>> a.flatatt()
    ' name="pippo" class="foo bla"'
    
Any Operation on this class is similar to jQuery.
'''
    def flatatt(self, **attrs):
        '''Return a string with atributes to add to the tag'''
        cs = ''
        attrs = self.attrs.copy()
        if self.classes:
            cs = ' '.join(self.classes)
            attrs['class'] = cs
        for k,v in self.data.items():
            attrs['data-{0}'.format(k)] = dump_data_value(v)
        if attrs:
            return flatatt(attrs)
        else:
            return ''
        
    @property
    def data(self):
        '''Dictionary of attributes.'''
        if not hasattr(self,'_HtmlAttrMixin__data'):
            self.__data = {}
        return self.__data
    
    def addData(self, name, val):
        if val:
            self.data[name] = val
        return self
    
    @property
    def attrs(self):
        '''Dictionary of attributes.'''
        if not hasattr(self,'_HtmlAttrMixin__attrs'):
            self.__attrs = {}
        return self.__attrs
    
    @property
    def classes(self):
        '''Set of classes.'''
        if not hasattr(self,'_HtmlAttrMixin__classes'):
            self.__classes = set()
        return self.__classes
    
    def addClass(self, cn):
        '''Add the specific class names to the class set and return ``self``.'''
        if cn:
            add = self.classes.add
            for cn in cn.split():
                cn = slugify(cn)
                add(cn)
        return self
    
    def addAttr(self, name, val):
        '''Add the specific attribute to the attribute dictionary
with key ``name`` and value ``value`` and return ``self``.'''
        self.attrs[name] = val
        return self
    
    def hasClass(self, cn):
        '''``True`` if ``cn`` is a class of self.'''
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
    '''Base class for HTML components.
It derives from :class:`djpcms.html.BaseMedia` and
:class:`djpcms.html.HtmlAttrMixin`. Anything which is rendered as HTML
is derived from this class.

:parameter tag: An optional HTML tag stored in the :attr:`tag` attribute.
:parameter cn: Optional HTML class names.
:parameter attributes: Optional attributes to add to the widget.

.. attribute:: tag

    A HTML tag.
    
    Default ``None``.
    
.. attribute:: is_hidden

    If ``True`` the widget is hidden.
    
    Default ``False``.
    
.. attribute:: inline

    If ``True`` the element is rendered as an inline element::
    
        <tag ..../>
        
    rather than::
    
        <tag ...>
         ....
        </tag>
    
    Default ``False``.
    
.. template:: optional template string or tuple for rendering the widget.

    Default: ``None``.
'''
    tag = None
    is_hidden = False
    default_style = None
    inline = False
    template = None
    attributes = {'id':None,'title':None}
    default_class = None
    
    def __init__(self, tag = None, cn = None, template = None, js = None,
                 renderer = None, css = None, default_style = None,
                 **attributes):
        attrs = self.attrs
        self.renderer = renderer
        self.tag = tag or self.tag
        self.template = template or self.template
        for attr,value in iteritems(self.attributes):
            if attr in attributes:
                value = attributes.pop(attr)
            attrp = 'process_{0}'.format(attr)
            if hasattr(self,attrp):
                value = getattr(self,attrp)(value)
            if value is not None:
                attrs[attr] = value
        if attributes:
            keys = list(attributes.keys())
            raise TypeError("__init__() got an unexpected keyword argument '{0}'".format(keys[0]))
        self.default_style = default_style or self.default_style
        if self.default_class:
            self.addClass(self.default_class)
        self.addClass(cn)
        media = self.media
        media.add_js(js)
        media.add_css(css)
    
    def ischeckbox(self):
        return False
        
    def render(self, *args, **kwargs):
        '''Render the widget.'''
        fattr = self.flatatt()
        html = self._render(fattr, *args, **kwargs)
        if self.renderer:
            return self.renderer(html)
        else:
            return html
    
    def _render(self, fattr, *args, **kwargs):
        if self.inline:
            return '<{0}{1}/>'.format(self.tag,fattr)
        else:
            if 'inner' in kwargs:
                inner = kwargs['inner']
            else:
                inner = self.inner(*args, **kwargs)
            if self.tag:
                return '<{0}{1}>\n{2}\n</{0}>'.format(self.tag,fattr,inner)
            else:
                return inner
    
    def get_context(self, context, *args, **kwargs):
        pass
    
    def inner(self, *args, **kwargs):
        '''Render the inner part of the widget. This is the part inside the
:attr:`tag` element. If the widget has not :attr:`tag`, this method is equivalent to
the :meth:`render` method.'''
        if self.template:
            context = {}
            self.get_context(context,*args,**kwargs)
            return loader.render(self.template,context)
        else:
            return ''
