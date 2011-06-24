import json

from py2py3 import iteritems

import djpcms
from djpcms import sites, UnicodeMixin, is_string, to_string
from djpcms.utils import force_str, slugify, escape, mark_safe
from djpcms.utils.structures import OrderedDict
from djpcms.utils.const import NOTHING
from djpcms.template import loader


__all__ = ['flatatt',
           'Renderer',
           'WidgetMaker',
           'Widget',
           'Html']

default_widgets_makers = {}

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


class Renderer(object):
    '''A mixin for all classes which render into html.

.. attribute:: description

    An optional description of the renderer.
    
    Default ``""``
'''
    
    description = None
    
    def render(self, *args, **kwargs):
        '''render ``self`` as html'''
        raise NotImplementedError
    
    def media(self):
        '''It returns an instance of :class:`djpcms.html.Media` or ``None``. It should be overritten by
derived classes.'''
        return None


class Widget(object):
    '''A class which exposes jQuery-alike API for
handling HTML classes, attributes and data on a html rendeble object::

    >>> a = Widget().addClass('bla foo').addAttr('name','pippo')
    >>> a.classes
    {'foo', 'bla'}
    >>> a.attrs
    {'name': 'pippo'}
    >>> a.flatatt()
    ' name="pippo" class="foo bla"'
    
Any Operation on this class is similar to jQuery.
'''    
    maker = None
    def __init__(self, maker = None, cn = None, data = None, **params):
        maker = maker if maker else self.maker
        if maker in default_widgets_makers:
            maker = default_widgets_makers[maker]
        if not isinstance(maker,WidgetMaker):
            maker = DefaultMaker
        self.maker = maker
        self.classes = set()
        self.data = data or {}
        self.attrs = attrs = maker.attrs.copy()
        self.addClass(maker.default_style)\
            .addClass(maker.default_class)\
            .addClass(cn)
        attributes = maker.attributes
        for att,val in iteritems(params):
            if att in attributes:
                attrs[att] = val
            
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
        
    def addData(self, name, val):
        if val:
            self.data[name] = val
        return self
    
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
    
    def render(self, djp = None, inner = None):
        return self.maker.render_from_widget(djp, self, inner)
    
    def inner(self, djp):
        return ''


class WidgetMaker(Renderer):
    '''Derived from :class:`djpcms.html.Renderer`,
it is a class used as factory for HTML components.

.. attribute:: tag

    A HTML tag (ex. ``div``, ``a`` and so forth)
    
    Default ``None``.
    
.. attribute:: is_hidden

    If ``True`` the widget is hidden.
    
    Default ``False``.

.. attribute:: default_style

    default css class style for the widget.
    
    Default ``None``.
        
.. attribute:: default_class

    default css class for the widget.
    
    Default ``None``.
    
.. attribute:: inline

    If ``True`` the element is rendered as an inline element::
    
        <tag ..../>
        
    rather than::
    
        <tag ...>
         ....
        </tag>
    
    Default ``False``.
    
.. attribute:: template

    optional template string for rendering the inner part of the widget.
    
    Default ``None``
    
.. attribute:: template_name

    optional template file name, or iterable over template file names,
    for rendering the widget. If :attr:`template` is available, this attribute
    has no effect.
    
.. attribute:: key

    An optional string which can be used to easily retrieve the
    element in the within other elements which holds it.
    If specified, the containing element will be an attribute named
    ``key`` with value given by this html widget.

    Default ``None``.
    
.. attribute:: allchildren

    A list containing al children.
    
.. attribute:: children

    A dictionary containing children with keys
    
.. attribute:: default

    Optional string which register the ``self`` as the default maker for
    the value of ``default``. For Example::
    
        >>> from djpcms import html
        >>> html.WidgetMaker('div', default='div')
        >>> html.WidgetMaker('a', default_class='ajax', default='a.ajax')
        >>> html.Widget('a.ajax', cn='ciao').render(inner='bla bla')
        <a class='ciao ajax'>bla bla</a>
        
    Default ``None``

'''
    tag = None
    key = None
    is_hidden = False
    default_style = None
    inline = False
    template = None
    template_name = None
    attributes = ('id',)
    default_class = None
    default_attrs = None
    _widget = None
    
    def __init__(self, tag = None, template = None,
                 renderer = None, inline = None,
                 default = False, description = '',
                 attributes = None, **params):
        if default:
            default_widgets_makers[default] = self
        self.attributes = set(self.attributes)
        if attributes:
            self.attributes.update(attributes)
        self.allchildren = []
        self.children = {}
        self.attrs = attrs = {}
        self.description = description or self.description
        self.renderer = renderer
        self.tag = tag or self.tag
        self.inline = inline if inline is not None else self.inline
        self.key = params.pop('key',self.key)
        self.template = params.pop('template',self.template)
        self.is_hidden = params.pop('is_hidden',self.is_hidden)
        self.template_name = params.pop('template_name',self.template_name)
        self.default_style = params.pop('default_style',self.default_style)
        self.default_class = params.pop('default_class',self.default_class)
        self._widget = self._widget or Widget
        if self.default_attrs:
            params.update(self.default_attrs)
        for attr in self.attributes:
            if attr in params:
                value = params.pop(attr)
                attrp = 'process_{0}'.format(attr)
                if hasattr(self,attrp):
                    value = getattr(self,attrp)(value)
                if value is not None:
                    attrs[attr] = value
        if params:
            keys = list(params)
            raise TypeError("__init__() got an unexpected keyword argument '{0}'".format(keys[0]))
    
    @classmethod
    def makeattr(cls, *attrs):
        attr = set(attrs)
        attr.update(cls.attributes)
        return attr
    
    def ischeckbox(self):
        '''Returns ``True`` if this is a checkbox widget.
Here because checkboxes have slighltly different way of rendering.
        '''
        return False
    
    def add(self,*widgets):
        '''Add children *widgets* to ``self``,
*widgets* must be instances of :class:`djpcms.html.WidgetMaker`.
If a child has an :attr:`djpcms.html.WidgetMaker.key` attribute specified,
it will be added to the ``children`` dictionary
for easy retrieval.
It returns self for concatenating data.'''
        for widget in widgets:
            if isinstance(widget,WidgetMaker):
                if not widget.default_style:
                    widget.default_style = self.default_style
                self.allchildren.append(widget)
                if widget.key:
                    self.children[widget.key] = widget
        return self
  
    def widget(self, *args, **kwargs):
        return self._widget(self, *args, **kwargs)
    
    def render(self, djp = None, inner = None, **kwargs):
        return self.widget(**kwargs).render(djp,inner)
    
    def render_from_widget(self, djp, widget, inner):
        fattr = widget.flatatt()
        if self.inline:
            html = '<{0}{1}/>'.format(self.tag,fattr)
        else:
            html = inner
            if html is None:
                html = self.inner(djp, widget)
            if self.tag:
                html = '<{0}{1}>{2}</{0}>'.format(self.tag,fattr,html)
        if self.renderer:
            html = self.renderer(html)
        if djp:
            djp.media += self.media()
        return html
    
    def inner(self, djp, widget):
        #Render the inner part of the widget
        if self.template or self.template_name:
            context = self.get_context(djp,widget)
            if self.template:
                raise NotImplemented
            else:
                return loader.render(self.template_name,context)
        else:
            return widget.inner(djp)

    def get_context(self, djp, widget):
        return {}
        
DefaultMaker = WidgetMaker()
    

class HtmlWrap(Widget):
    
    def __init__(self, *args, **kwargs):
        self._inner = kwargs.pop('inner','')
        super(HtmlWrap,self).__init__(*args, **kwargs)
        
    def inner(self, *args, **kwargs):
        if hasattr(self._inner,'render'):
            return self._inner.render(*args, **kwargs)
        else:
            return to_string(self._inner)


class Html(WidgetMaker):
    '''A :class:`FormLayoutElement` which renders to `self`.'''
    def __init__(self, html = '', renderer = None, **kwargs):
        super(Html,self).__init__(**kwargs)
        self.html = html

    def inner(self, *args, **kwargs):
        return self.html
