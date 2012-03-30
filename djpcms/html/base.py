import json
from copy import copy, deepcopy
from inspect import isgenerator

from djpcms.utils.py2py3 import UnicodeMixin, is_string, to_string,\
                                is_bytes_or_string, iteritems
from djpcms.utils import slugify, escape, mark_safe, lazymethod, iterable,\
                         NOTHING
from djpcms.utils.structures import OrderedDict

from .context import ContextRenderer, StreamContextRenderer


__all__ = ['flatatt',
           'Renderer',
           'LazyHtml',
           'WidgetMaker',
           'Widget',
           'Html',
           'NON_BREACKING_SPACE']

    
default_widgets_makers = {}

NON_BREACKING_SPACE = mark_safe('&nbsp;')

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
        raise NotImplementedError()
    
    def media(self, request):
        '''It returns an instance of :class:`Media`.
It should be overritten by derived classes.'''
        return None
    

class LazyHtml(UnicodeMixin):
    '''A lazy wrapper for html components
    '''
    def __init__(self, request, elem):
        self.request = request
        self.elem = elem
    
    @lazymethod
    def __unicode__(self):
        return mark_safe(self.elem.render(self.request))
    
    
def update(container, target):
    if container:
        container = deepcopy(container)
        if target:
            container.update(target)
        return container
    return target
    

class AttributeMixin(object):
    classes = None
    data = None
    
    def __init__(self, cn = None, data = None):
        self.classes = update(self.classes,set())
        self.data = update(self.data,{})
        self.addData(data)
        self.addClass(cn)
    
    def addClass(self, cn):
        '''Add the specific class names to the class set and return ``self``.'''
        if isinstance(cn,(tuple,list,set,frozenset)):
            self.classes.update(cn)
        elif cn:
            add = self.classes.add
            for cn in cn.split():
                cn = slugify(cn)
                add(cn)
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
    
    def addData(self, name, val = None):
        '''Add/updated the data attribute.'''
        if val is not None:
            if name in self.data:
                val0 = self.data[name]
                if isinstance(val0, dict) and isinstance(val, dict):
                    val0.update(val)
                    return self
        elif isinstance(name, dict):
            add = self.addData
            for n,v in name.items():
                add(n, v)
            return self
        if name:
            self.data[name] = val
        return self
    
    
class Widget(AttributeMixin):
    '''A class which exposes jQuery-alike API for
handling HTML classes, attributes and data on a html object::

    >>> a = Widget('div').addClass('bla foo').addAttr('name','pippo')
    >>> a.classes
    {'foo', 'bla'}
    >>> a.attrs
    {'name': 'pippo'}
    >>> a.flatatt()
    ' name="pippo" class="foo bla"'

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
        '''Initialize a widget. Usually this constructor is not invoked
directly, Instead it is called by the callable :class:`WidgetMaker` which
is a factory of :class:`Widget`.

:parameter maker: The :class:`WidgetMaker` creating this :class:`Widget`.
:parameter data_stream: set the :attr:`data_stream` attribute.
'''
        maker = maker if maker else self.maker
        if maker in default_widgets_makers:
            maker = default_widgets_makers[maker]
        if not isinstance(maker,WidgetMaker):
            maker = DefaultMaker
        cn = update(maker.classes, cn)
        data = update(maker.data, data)            
        super(Widget,self).__init__(cn = cn, data = data)
        self.maker = maker
        self._css = css or {}
        self.attrs = attrs = maker.attrs.copy()
        self.addClass(maker.default_style).addClass(maker.default_class)
        self.classes.update(maker.classes)
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
    
    def css(self, mapping):
        '''Upsate the css dictionary if *mapping* is a dictionary, otherwise
 return the css value at *mapping*.'''
        if isinstance(mapping,dict):
            self._css.update(mapping)
            return self
        else:
            return self._css.get(mapping)
    
    def addAttr(self, name, val):
        '''Add the specific attribute to the attribute dictionary
with key ``name`` and value ``value`` and return ``self``.'''
        self.attrs[name] = val
        return self
    
    def addAttrs(self, mapping):
        if mapping:
            self.attrs.update(mapping)
        return self
    
    def attr(self, name):
        return self.attrs.get(name,None)
    
    def add(self, *args, **kwargs):
        '''Add to the stream. This functions delegates the adding to the
 :meth:`WidgetMaker.add_to_widget` method.'''
        self.maker.add_to_widget(self,*args,**kwargs)
    
    def render(self, request = None, context = None):
        '''Render the widget. It accept two optional parameters, a http
request object and a dictionary for rendering children with a key.
        
:parameter request: Optional request object.
:parameter request: Optional context dictionary.
'''
        context = context if context is not None else {}
        return self.maker.render_from_widget(request, self, context)
    
    def hide(self):
        '''Set the ``css`` ``display`` property to ``none`` and return self
for concatenation.'''
        self.css({'display':'none'})
        return self
        
    def show(self):
        self.css.pop('display',None)
        return self
        
    @property
    def html(self):
        if not hasattr(self,'_html'):
            self._html = self.render()
        return self._html
    

class WidgetMaker(Renderer, AttributeMixin):
    '''A :class:`Renderer` used as factory for :class:`Widget` instances.
It is general enough that it can be use for a vast array of HTML widgets. For
corner cases, users can subclass it to customize behavior. 

:parameter inline: Its value is stored in the :attr:`inline` attribute.
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
    
.. attribute:: allchildren

    A list containing all :class:`WidgetMaker` instances which are children
    of the instance.
    
.. attribute:: children

    A dictionary containing children with keys.
    
.. attribute:: parent

    The ancestor of this :class:`WidgetMaker`. This attribute is assigned by
    the API when a :class:`WidgetMaker` is added to another :class:`WidgetMaker`
    via the :meth:`WidgetMaker.add`.
    
    default: ``None``
    
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
    parent = None
    is_hidden = False
    default_style = None
    inline = False
    attributes = ('id','title','dir','style')
    default_class = None
    default_attrs = None
    _widget = None
    _template = to_string('<{0}{1}>{2}</{0}>')
    
    def __init__(self, inline = None, default = False,
                 description = '', widget = None,
                 attributes = None, renderer = None,
                 data2html = None, media = None,
                 data = None, cn = None, key = None,
                 **params):
        AttributeMixin.__init__(self, cn = cn, data = data)
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
        self.is_hidden = params.pop('is_hidden',self.is_hidden)
        self.tag = params.pop('tag',self.tag)
        self.key = key
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
        # the remaining parameters are added to the data dictionary
        self.data.update(params)
        if not default and self.tag and self.tag not in default_widgets_makers:
            default = self.tag
        if default:
            default_widgets_makers[default] = self
    
    def __call__(self, data_stream = None, cn = None,
                 data = None, css = None, **params):
        return self._widget(self,
                            data_stream = data_stream,
                            cn = cn,
                            data = data,
                            css = css,
                            **params)
        
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
        '''Add children *widgets* to this class:`WidgetMaker`.
*widgets* must be class:`WidgetMaker`.'''
        for widget in widgets:
            if isinstance(widget, WidgetMaker):
                if not widget.default_style:
                    widget.default_style = self.default_style
                self.allchildren.append(widget)
                widget.parent = self
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

    def keys(self):
        '''generator of context keywords'''
        for child in self.allchildren:
            for key in child.keys():
                yield key
        if self.key:
            yield self.key 
                    
    def get_context(self, request, widget, context):
        '''Called by the :meth:`inner` method to build extra context.
By default it return *context*.'''
        return context
    
    def render_from_widget(self, request, widget, context):
        '''Render the *widget* using the *context* dictionary and
information contained in this :class:`WidgetMaker`.'''
        if self.inline:
            if widget.tag:
                fattr = widget.flatatt()
                text = '<' + self.tag + fattr + '/>'
            else:
                text = ''
        else:
            text = self.inner(request, widget, context)
            if widget.tag:
                fattr = widget.flatatt()
                if isinstance(text, ContextRenderer):
                    text.add_renderer(
                        lambda c : self._template.format(widget.tag,fattr,c))
                else:
                    text = self._template.format(widget.tag, fattr, text)
        if request:
            request.media.add(self.media(request))
        if isinstance(text, ContextRenderer):
            text.add_renderer(mark_safe)
            return text.done()
        else:
            return mark_safe(text)
    
    def inner(self, request, widget, context):
        '''Render the inner part of the widget (it exclude the outer tag). 

:parameter widget: instance of :class:`Widget` to be rendered
:parameter context: A dictionary of data for rendering.
:rtype: A string representing the inner part of the widget or
    a :class:`ContextRenderer` if asynchronous data is found.
'''
        context = self.get_context(request, widget, context)
        return StreamContextRenderer(request,
                        self.stream(request, widget, context))
    
    def stream(self, request, widget, context):
        '''This method is called by :meth:`inner` method.
It returns an iterable over chunks of html
to be displayed in the inner part of the widget.
This method can be overridden by subclasses if a specific behavior
is required.

First, data in :attr:`data_stream` is rendered. Second, children of the
widget are rendered.

:rtype: a generator of strings and :class:`ContextRenderer`.
'''
        data2html = self.data2html
        if self in context:
            context_data = context[self]
        elif self.key and self.key in context:
            context_data = context[self.key]
        else:
            context_data = None
            
        if context_data is not None and not iterable(context_data):
            context_data = (context_data,) 
               
        # First we render the stream of data in the widget,
        # second the context data
        for data in (widget.data_stream, context_data):
            if data:
                for chunk in data:
                    yield data2html(request, chunk)
                    
        # Subsequently we render children
        for w in self.children_widgets(widget):
            chunk = w.render(request, context)
            yield data2html(request, chunk)
        
    def data2html(self, request, data):
        '''Process data from :meth:`stream`. By default it renders data if
 data is an instance of :class:`Widget` and returns it.'''
        if isinstance(data, Widget):
            data = data.render(request)
        if isinstance(data, ContextRenderer):
            data = data.done()
        return data

    def children_widgets(self, widget):
        # Internal function for creating child widgets
        for child in self.allchildren:
            yield self.child_widget(child, widget)
            
    def child_widget(self, child_maker, widget, **kwargs):
        '''Function invoked when there are children available. See the
:attr:`allchildren`` attribute for more information on children.

:parameter child_maker: a :class:`WidgetMaker` child of self.
:parameter widget: The :class:`Widget` instance used for rendering.
:parameter kwargs: extra key-valued parameters to passed to the child
    widget constructor.
:rtype: An instance of :class:`Widget` for the child element.
'''
        w = child_maker(**widget.internal)
        w.internal.update(kwargs)
        w.internal['parent'] = widget
        return w
    
    def media(self, request):
        return self._media
        
        
DefaultMaker = WidgetMaker()


class Html(WidgetMaker):
    '''A :class:`FormLayoutElement` which renders to `self`.'''
    def __init__(self, inner = None, **kwargs):
        self._inner = inner
        super(Html,self).__init__(**kwargs)

    def stream(self, request, widget, context):
        if self._inner is not None:
            yield self._inner
        for v in super(Html,self).stream(request, widget, context):
            yield v
