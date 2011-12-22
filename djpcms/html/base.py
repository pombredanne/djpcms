import json
from copy import copy
from inspect import isgenerator

from py2py3 import iteritems

import djpcms
from djpcms import UnicodeMixin, is_string, to_string, is_bytes_or_string
from djpcms.utils import force_str, slugify, escape, mark_safe, lazymethod
from djpcms.utils.structures import OrderedDict
from djpcms.utils.const import NOTHING

from .context import ContextRenderer, StreamContextRenderer


__all__ = ['flatatt',
           'Renderer',
           'LazyHtml',
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


def iterable_for_widget(data):
    if not isinstance(data,Widget) and hasattr(data,'__iter__'):
        return not is_bytes_or_string(data)


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
    
    def media(self, request):
        '''It returns an instance of :class:`Media`.
It should be overritten by derived classes.'''
        return None
    

class LazyHtml(djpcms.UnicodeMixin):
    '''A lazy wrapper for html components
    '''
    def __init__(self, request, elem):
        self.request = request
        self.elem = elem
    
    @lazymethod
    def __unicode__(self):
        return mark_safe(self.elem.render(self.request))
    

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

.. attribute:: data_stream

    A list of children for the widget.
    
.. attribute:: parent

    The parent :class:`Widget` holding ``self``.
    
    Default ``None``
    
.. attribute:: root

    The root :class:`Widget` of the tree where ``self`` belongs to. This is
    obtained by recursively navigating up the :attr:`parent` attribute.
    If the element has no :attr:`parent`, return ``self``.
'''    
    maker = None
    def __init__(self, maker = None, data_stream = None,
                 cn = None, data = None, options = None, 
                 css = None, **params):
        maker = maker if maker else self.maker
        if maker in default_widgets_makers:
            maker = default_widgets_makers[maker]
        if not isinstance(maker,WidgetMaker):
            maker = DefaultMaker
        self.maker = maker
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
        if data_stream is not None:
            if iterable_for_widget(data_stream):
                for d in data_stream:
                    self.add(d)
            else:
                self.add(data_stream)
        
    def __repr__(self):
        if self.tag:
            return '<' + self.tag + self.flatatt() + '>'
        else:
            return '{0}({1})'.format(self.__class__.__name__,self.maker)
    
    def __len__(self):
        return len(self.data_stream)
    
    def __iter__(self):
        return iter(self.data_stream)
    
    @property
    def parent(self):
        return self.internal.get('parent')
    
    @property
    def root(self):
        p = self.parent
        if p is not None:
            return p.root
        else:
            return self
    
    @property
    def data_stream(self):
        if 'data_stream' not in self.internal:
            self.internal['data_stream'] = []
        return self.internal['data_stream']
    
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
        '''Upsate the css dictionary if *mapping* is a dictionary, otherwise
 return the css value at *mapping*.'''
        if isinstance(mapping,dict):
            self._css.update(mapping)
            return self
        else:
            return self._css.get(mapping)
        
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
    
    def add(self, *args, **kwargs):
        '''Add to the stream. This functions delegates the adding to the
 :meth:`WidgetMaker.add_to_widget` method.'''
        self.maker.add_to_widget(self,*args,**kwargs)
        
    def get_context(self, request, context = None):
        '''Return the context dictionary for this widget.'''
        context = context if context is not None else {}
        return self.maker.get_context(request, self, context)
    
    def render(self, request = None, context = None):
        '''Render the widget'''
        context = context if context is not None else {}
        return self.maker.render_from_widget(request, self, context)
    
    def hide(self):
        self.css({'display':'none'})
        
    @property
    def html(self):
        if not hasattr(self,'_html'):
            self._html = self.render()
        return self._html
    


class WidgetMaker(Renderer):
    '''A :class:`Renderer` used as factory for :class:`Widget` instances.
It is general enough that it can be use for a vast array of HTML widgets. For
corner cases, users can subclass it to customize behavior. 

:parameter inline: Its value is stored in the :attr:`inline` attribute.
:parameter renderer: Its value is stored in the :attr:`renderer` attribute.
:parameter widget: Optional :class:`Widget` class which overrides the default.
    
--


**WidgetMaker Attributes**


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
    

.. attribute:: renderer

    Optional callable for rendering the inner part of the widget.
    
    Default ``None``
    
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

    A list containing all :class:`WidgetMaker` instances which are children
    of the instance.
    
.. attribute:: children

    A dictionary containing children with keys.
    
.. attribute:: widget_class

    The widget class used by the :meth:`widget` method when creating widgets.
    
    Default: :class:`Widget`
    
.. attribute:: default

    Optional string which register the ``self`` as the default maker for
    the value of ``default``. For Example::
    
        >>> from djpcms import html
        >>> html.WidgetMaker('div', default='div')
        >>> html.WidgetMaker('a', default_class='ajax', default='a.ajax')
        >>> html.Widget('a.ajax', cn='ciao').render(inner='bla bla')
        <a class='ciao ajax'>bla bla</a>
        
    Default ``None``

--


**WidgetMaker Methods**

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
                 attributes = None, renderer = None,
                 data2html = None, media = None,
                 **params):
        self.attributes = set(self.attributes)
        if attributes:
            self.attributes.update(attributes)
        self.allchildren = []
        self.children = {}
        self.attrs = attrs = {}
        self._media = media
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
        if data2html:
            self.data2html =\
                     lambda request, data : data2html(self, request, data)
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
    
    @property
    def widget_class(self):
        return self._widget
    
    @classmethod
    def makeattr(cls, *attrs):
        attr = set(attrs)
        attr.update(cls.attributes)
        return attr
    
    def __repr__(self):
        return '{0}{1}'.format(self.__class__.__name__,'-'+\
                               self.tag if self.tag else '')
    
    def add(self, *widgets):
        '''Add children *widgets* to ``self``,
*widgets* must be instances of :class:`WidgetMaker`.
If a child has an :attr:`WidgetMaker.key` attribute specified,
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
  
    def add_to_widget(self, widget, element):
        '''Called by *widget* to add a new *element* to its data stream.
 By default it simply append *element* to the :attr:`Widget.data_stream`
 attribute. It can be overwritten but call super for consistency.'''
        if isinstance(element,Widget):
            element.internal['parent'] = widget
        widget.data_stream.append(element)
        
    def widget(self, **kwargs):
        '''Create an instance of a :class:`Widget` for rendering.
 It invokes the constructor of the :attr:`widget_class` attribute.'''
        kwargs.pop('maker',None)
        return self._widget(self, **kwargs)
    
    def children_widgets(self, widget):
        for child in self.allchildren:
            yield self.child_widget(child, widget)
            
    def get_context(self, request, widget, context):
        '''Called by the :meth:`inner` method it
returns a dictionary of variables used for rendering. By default it
loops over the :attr:`allchildren` list and put the rendered child
in a new list.
This child rendered list is available at `children` key in the returned
dictionary.'''
        ctx = widget.internal
        children = []
        for w in self.children_widgets(widget):
            key = w.maker.key
            if key and key in context:
                w.add(context.pop(key))
            children.append(w.render(request,context))
        ctx['children'] = children
        return ctx
    
    def render_from_widget(self, request, widget, context):
        if self.inline:
            if widget.tag:
                fattr = widget.flatatt()
                text = '<{0}{1}/>'.format(self.tag,fattr)
            else:
                text = ''
        else:
            text = self.inner(request, widget, context)
            if widget.tag:
                fattr = widget.flatatt()
                if isinstance(text,ContextRenderer):
                    text.add_renderer(
                        lambda c : self._template.format(widget.tag,fattr,c))
                else:
                    text = self._template.format(widget.tag,fattr,text)
        if request:
            request.media.add(self.media(request))
        if isinstance(text,ContextRenderer):
            text.add_renderer(self.renderer)
            text.add_renderer(mark_safe)
            return text.done()
        else:
            if self.renderer:
                text = self.renderer(text)
            return mark_safe(text)
    
    def inner(self, request, widget, context):
        '''Render the inner part of the widget (it exclude the outer tag). 

:parameter widget: instance of :class:`Widget` to be rendered
:parameter keys: ???
:return: A string representing the inner part of the widget.

By default it renders the :attr:`template` or :attr:`template_name`
if available, otherwise it returns a :class:`StreamContextRenderer`
from the :meth:`stream` method.
'''
        context = self.get_context(request,widget,context)
        if self.template or self.template_name:
            context.update({'maker':self,
                            'widget':widget})
            if request is None:
                raise ValueError('No request. Cannot render template.')
            lt = request.view.template
            if self.template:
                return lt.template_class(self.template).render(context)
            else:
                return lt.render(self.template_name,context)
        else:
            return StreamContextRenderer(request,
                                         self.stream(request,widget,context))
    
    def stream(self, request, widget, context):
        '''This method is called by :meth:`inner` when rendering
without templates. It returns an iterable over chunks of html
to be displayed in the inner part of the widget.
This method can be overridden by subclasses if a specific behaviour
is required.'''
        data2html = self.data2html
        if widget.data_stream:
            for chunk in widget.data_stream:
                yield data2html(request, chunk)
        for child in context['children']:
            yield data2html(request, child)
        
    def data2html(self, request, data):
        '''Process data from :meth:`stream`. By default it renders data if
 data is an instance of :class:`Widget` and returns it.'''
        if isinstance(data,Widget):
            data = data.render(request)
        if isinstance(data,ContextRenderer):
            data = data.done()
        return data

    def child_widget(self, child, widget, **kwargs):
        '''Function invoked when there are children available. See the
:attr:`allchildren`` attribute for more information on children.

:parameter child: a :class:`WidgetMaker` child of self.
:parameter widget: The :class:`Widget` instance used for rendering.
:parameter kwargs: extra key-valued parameters to passed to the child
    widget constructor.
:rtype: An instance of :class:`Widget` for the child element.
'''
        w = child.widget(**widget.internal)
        w.internal.update(kwargs)
        w.internal['parent'] = widget
        return w    
    
    def ischeckbox(self):
        '''Returns ``True`` if this is a checkbox widget.
Here because checkboxes have slighltly different way of rendering.
        '''
        return False
    
    def media(self, request):
        return self._media
        
        
DefaultMaker = WidgetMaker()


class Html(WidgetMaker):
    '''A :class:`FormLayoutElement` which renders to `self`.'''
    pass
