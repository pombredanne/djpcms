import json
from copy import copy

from py2py3 import iteritems

import djpcms
from djpcms import UnicodeMixin, is_string, to_string, ContextRenderer
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
    
    def media(self, djp = None):
        '''It returns an instance of :class:`djpcms.html.Media`.
It should be overritten by derived classes.'''
        return None


class Widget(object):
    '''A class which exposes jQuery-alike API for
handling HTML classes, attributes and data on a html object::

    >>> a = Widget('div').addClass('bla foo').addAttr('name','pippo')
    >>> a.classes
    {'foo', 'bla'}
    >>> a.attrs
    {'name': 'pippo'}
    >>> a.flatatt()
    ' name="pippo" class="foo bla"'
    
Any Operation on this class is similar to jQuery.
'''    
    maker = None
    def __init__(self, maker = None, cn = None, data = None,
                 options = None, data_stream = None,
                 css = None, **params):
        maker = maker if maker else self.maker
        if maker in default_widgets_makers:
            maker = default_widgets_makers[maker]
        if not isinstance(maker,WidgetMaker):
            maker = DefaultMaker
        self.maker = maker
        self.data_stream = data_stream
        self.classes = set()
        self._css = css or {}
        self.data = data or {}
        self.attrs = attrs = maker.attrs.copy()
        self.addClass(maker.default_style)\
            .addClass(maker.default_class)\
            .addClass(cn)
        attributes = maker.attributes
        for att in list(params):
            if att in attributes:
                attrs[att] = params.pop(att)
        self.internal = params
        self.tag = self.maker.tag
        
    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__,self.maker)
    
    @property
    def parent(self):
        return self.internal.get('parent',None)
    
    def copy(self, **kwargs):
        c = copy(self)
        c.internal.update(kwargs)
        return c
        
    def flatatt(self, **attrs):
        '''Return a string with atributes to add to the tag'''
        cs = ''
        attrs = self.attrs.copy()
        if self.classes:
            cs = ' '.join(self.classes)
            attrs['class'] = cs
        if self._css:
            attrs['style'] = ''.join(('{0}:{1};'.format(k,v)\
                                       for k,v in self._css.items()))
        for k,v in self.data.items():
            attrs['data-{0}'.format(k)] = dump_data_value(v)
        if attrs:
            return flatatt(attrs)
        else:
            return ''
        
    def addData(self, name, val = None):
        '''Add/updated the data attribute.'''
        if val:
            if name in self.data:
                val0 = self.data[name]
                if isinstance(val0,dict) and isinstance(val,dict):
                    val0.update(val)
                    return self
        elif isinstance(name,dict):
            add = self.addData
            for n,v in name.items():
                add(n, v)
            return self
        if name:
            self.data[name] = val
        return self
    
    def css(self, mapping):
        self._css.update(mapping)
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
    
    def addAttrs(self, mapping):
        self.attrs.update(mapping)
        return self
    
    def attr(self, name):
        return self.attrs.get(name,None)
    
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
    
    def render(self, djp = None, inner = None, keys = None, **kwargs):
        ctx = self.maker.render_from_widget(djp, self, inner, keys or kwargs)
        ctx.add_renderer(mark_safe)
        return ctx.done()
    
    @property
    def html(self):
        if not hasattr(self,'_html'):
            self._html = self.render()
        return self._html


class WidgetMaker(Renderer):
    '''Derived from :class:`djpcms.html.Renderer`,
it is a class used as factory for HTML components.

:parameter inline: If ``True`` the widget is rendered as an inline element::
    Its value is stored in the :attr:`inline`.
    
    Default ``False``.

.. attribute:: tag

    A HTML tag (ex. ``div``, ``a`` and so forth)
    
    Default ``None``.
    
.. attribute:: attributes

    List of attributes supported by the widget.
    
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
    
        <tag ....>
        
    rather than::
    
        <tag ...>
         ....
        </tag>
    
.. attribute:: template

    optional template string for rendering the inner part of the widget.
    Use with care as it slow down the rendering.
    
    Default ``None``.
    
.. attribute:: template_name

    optional template file name, or iterable over template file names,
    for rendering the widget. If :attr:`template` is available, this attribute
    has no effect.
    Use with care as it slow down the rendering.
    
    default ``None``.
    
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
    attributes = ('id','title','dir','style')
    default_class = None
    default_attrs = None
    _widget = None
    _template = to_string('<{0}{1}>{2}</{0}>')
    
    def __init__(self, inline = None, default = False,
                 description = '', widget = None,
                 attributes = None, inner = None,
                 renderer = None, **params):
        self.attributes = set(self.attributes)
        if attributes:
            self.attributes.update(attributes)
        self.allchildren = []
        self.children = {}
        self.attrs = attrs = {}
        self.description = description or self.description
        self.renderer = renderer
        self.inline = inline if inline is not None else self.inline
        self.key = params.pop('key',self.key)
        self.template = params.pop('template',self.template)
        self.is_hidden = params.pop('is_hidden',self.is_hidden)
        self.tag = params.pop('tag',self.tag)
        self.template_name = params.pop('template_name',self.template_name)
        self.default_style = params.pop('default_style',self.default_style)
        self.default_class = params.pop('default_class',self.default_class)
        self._widget = widget or self._widget or Widget
        self._inner = inner
        if self.default_attrs:
            p = self.default_attrs.copy()
            p.update(params)
            params = p
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
            raise TypeError("__init__() got an unexpected keyword argument\
 '{0}'".format(keys[0]))
        key = None
        if default:
            key = default
        elif self.tag not in default_widgets_makers:
            key = self.tag
        
        if key:
            default_widgets_makers[key] = self
    
    @classmethod
    def makeattr(cls, *attrs):
        attr = set(attrs)
        attr.update(cls.attributes)
        return attr
    
    def __repr__(self):
        return '{0}{1}'.format(self.__class__.__name__,'-'+\
                               self.tag if self.tag else '')
    
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
  
    def widget(self, **kwargs):
        '''Create an instance of a :class:`djpcms.html.Widget` for rendering.'''
        return self._widget(self, **kwargs)
    
    def render(self, djp = None, inner = None, **kwargs):
        return self.widget(**kwargs).render(djp,inner)
    
    def render_from_widget(self, djp, widget, inner, keys):
        if self.inline:
            if widget.tag:
                fattr = widget.flatatt()
                text = '<{0}{1}/>'.format(self.tag,fattr)
            else:
                text = ''
            text = ContextRenderer.make(text)
        else:
            text = inner or self._inner
            if text is None:
                text = self.inner(djp, widget, keys)
            text = ContextRenderer.make(text)
            if widget.tag:
                fattr = widget.flatatt()
                text.add_renderer(
                    lambda c : self._template.format(widget.tag,fattr,c))
        text.add_renderer(self.renderer)
        if djp:
            djp.media.add(self.media(djp))
        return text
    
    def inner(self, djp, widget, keys):
        '''Render the inner part of the widget. This can be overwritten by
derived classes and should return the inner part of html.
By default it renders the template if it is available, otherwise
an empty string.'''
        context = self.get_context(djp,widget,keys)
        if self.template or self.template_name:
            context.update({'maker':self,
                            'widget':widget})
            lt = djp.site.template if djp else loader
            if self.template:
                return lt.template_class(self.template).render(context)
            else:
                return lt.render(self.template_name,context)
        else:
            return '\n'.join(self.stream(djp,widget,context))
    
    def stream(self, djp, widget, context):
        '''This method is called when rendering without templates.
It returns an iterable over chunks of html to be displayed in the
inner part of the widget.'''
        if widget.data_stream:
            data2html = self.data2html
            for chunk in widget.data_stream:
                yield data2html(chunk)
        for child in context['children']:
            yield child
        
    def data2html(self, data):
        return data

    def child_widget(self, child, widget, **kwargs):
        w = child.widget(**widget.internal)
        w.internal.update(kwargs)
        w.internal['parent'] = widget
        return w
    
    def get_context(self, djp, widget, keys):
        '''Function called by :meth:`inner` method when the widget needs to be rendered via a template.
It returns a dictionary of variables to be passed to the template engine.'''
        ctx = widget.internal
        # Loop over fields and delivers the goods
        children = []
        for child in self.allchildren:
            w = self.child_widget(child, widget)
            key = w.maker.key
            if key and key in keys:
                text = w.render(djp, keys[key])
            else:
                text = w.render(djp, keys = keys)
                #if key:
                #    ctx[key] = text
                #    continue
            children.append(text)
        ctx['children'] = children
        return ctx
        
        
DefaultMaker = WidgetMaker()


class Html(WidgetMaker):
    '''A :class:`FormLayoutElement` which renders to `self`.'''
    def __init__(self, html = '', renderer = None, **kwargs):
        super(Html,self).__init__(**kwargs)
        self.html = html

    def inner(self, *args, **kwargs):
        return self.html
