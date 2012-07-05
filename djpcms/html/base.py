import json
import traceback
from inspect import istraceback
from copy import copy, deepcopy

from djpcms import Renderer
from djpcms.utils.text import slugify, escape, mark_safe
from djpcms.utils.decorators import lazymethod
from djpcms.utils.structures import OrderedDict
from djpcms.utils.async import MultiDeferred, Deferred, async_object
from djpcms.utils.httpurl import ispy3k, is_string, to_string, iteritems,\
                                 is_string_or_native_string, itervalues

if ispy3k:
    from itertools import zip_longest
else:   # pragma nocover
    from itertools import izip_longest as zip_longest

__all__ = ['flatatt',
           'render',
           'html_trace',
           'StreamRenderer',
           'WidgetMaker',
           'Text',
           'Widget',
           'Div',
           'Anchor',
           'Img',
           'NON_BREACKING_SPACE']

    
default_widgets_makers = {}

NON_BREACKING_SPACE = mark_safe('&nbsp;')

def attrsiter(attrs):
    NOTHING = ('', None)
    for k,v in attrs.items():
        if v not in NOTHING:
            yield " {0}='{1}'".format(k, escape(v,force=True))

                
def flatatt(attrs):
    return ''.join(attrsiter(attrs))

def render(request, data):
    if isinstance(data, Widget):
        return data.render(request)
    else:
        return data
    
def dump_data_value(v):
    if not is_string(v):
        if isinstance(v,bytes):
            v = v.decode()
        else:
            v = json.dumps(v)
    return mark_safe(v)


def iterable_for_widget(data):
    if isinstance(data, dict):
        return iteritems(data)
    elif not isinstance(data, Widget) and hasattr(data,'__iter__') and\
         not is_string_or_native_string(data):
        return data
    else:
        return (data,)
    
def update(container, target):
    if container:
        container = deepcopy(container)
        if target:
            container.update(target)
        return container
    return target
    
def html_trace(exc_info, plain=False):
    if exc_info:
        error = Widget()
        ptag = None if plain else 'p'
        trace = exc_info[2]
        if istraceback(trace):
            trace = traceback.format_exception(*exc_info)
        for traces in trace:
            counter = 0
            for trace in traces.split('\n'):
                if trace.startswith('  '):
                    counter += 1
                    trace = trace[2:]
                if not trace:
                    continue
                w = Widget(ptag, escape(trace))
                if counter:
                    w.css({'margin-left':'{0}px'.format(20*counter)})
                error.add(w)
        return error.render()


class StreamRenderer(Deferred):
    
    def __init__(self, stream, renderer=None, **params):
        super(StreamRenderer, self).__init__()
        self._m = MultiDeferred(stream, fireOnOneErrback=True, **params)\
                    .lock().addBoth(self.callback)
        self.renderer = renderer
        self.add_callback(self.post_process).add_callback(mark_safe)
            
    def post_process(self, stream):
        if self.renderer:
            return self.renderer(stream)
        else:
            return ''.join(self._post_process(stream))
        
    def _post_process(self, stream):
        for value in stream:
            if value is None:
                continue
            elif isinstance(value, bytes):
                yield value.decode('utf-8')
            elif isinstance(value, str):
                yield value
            else:
                yield str(value)
            
            
class AttributeMixin(object):
    classes = None
    data = None
    attrs = None
    _css = None
    
    def __init__(self, cn=None, data=None, attrs=None, css=None):
        classes = self.classes
        self.classes = set()
        self.data = update(self.data,{})
        self.attrs = update(self.attrs,{})
        self._css = update(self._css,{})
        self.addData(data)
        self.addClass(classes)
        self.addClass(cn)
        self.addAttrs(attrs)
        self.css(css)
        self.children = OrderedDict()
        self.internal = {} 
    
    def __getitem__(self, key):
        return self.children[key]
    
    def allchildren(self):
        return itervalues(self.children)
    
    def addAttr(self, name, val):
        '''Add the specific attribute to the attribute dictionary
with key ``name`` and value ``value`` and return ``self``.'''
        if val is not None:
            self.attrs[name] = val
        return self
    
    def addAttrs(self, mapping):
        if mapping:
            self.attrs.update(mapping)
        return self
    
    def attr(self, name):
        return self.attrs.get(name, None)
    
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
    
    def css(self, mapping=None):
        '''Update the css dictionary if *mapping* is a dictionary, otherwise
 return the css value at *mapping*.'''
        if mapping is None:
            return self._css
        elif isinstance(mapping, dict):
            self._css.update(mapping)
            return self
        else:
            return self._css.get(mapping)
    
    
class Text(Renderer):
    
    def __init__(self, text, content_type='text/html'):
        self._content_type = content_type
        self.data = text
    
    def content_type(self):
        return self._content_type
        
    def render(self, *args, **kwargs):
        return self.data
    
    
class Widget(Renderer, AttributeMixin):
    '''A class which exposes jQuery-alike API for
handling HTML classes, attributes and data on a html element::

    >>> a = Widget('div').addClass('bla foo').addAttr('name','pippo')
    >>> a.classes
    {'foo', 'bla'}
    >>> a.attrs
    {'name': 'pippo'}
    >>> a.flatatt()
    ' name="pippo" class="foo bla"'

.. attribute:: data_stream
    A list data elements 
    
.. attribute:: parent

    The parent :class:`Widget` holding ``self``.
    
    Default ``None``
    
.. attribute:: root

    The root :class:`Widget` of the tree where ``self`` belongs to. This is
    obtained by recursively navigating up the :attr:`parent` attribute.
    If the element has no :attr:`parent`, return ``self``.
'''    
    maker = None
    _streamed = False
    def __init__(self, maker=None, data_stream=None,
                 cn=None, data=None, options=None, 
                 css=None, **params):
        '''Initialize a widget. Usually this constructor is not invoked
directly, Instead it is called by the callable :class:`WidgetMaker` which
is a factory of :class:`Widget`.

:parameter maker: The :class:`WidgetMaker` creating this :class:`Widget`.
:parameter data_stream: set the :attr:`data_stream` attribute.
'''
        maker = maker if maker else self.maker
        if maker in default_widgets_makers:
            maker = default_widgets_makers[maker]
        if not isinstance(maker, WidgetMaker):
            maker = DefaultMaker
        cn = update(maker.classes, cn)
        data = update(maker.data, data)
        css = update(maker.css(), css)
        AttributeMixin.__init__(self, cn=cn, data=data,
                                attrs=maker.attrs, css=css)
        self.maker = maker
        self._data_stream = []
        self.addClass(maker.default_style)
        attributes = maker.attributes
        for att in list(params):
            if att in attributes:
                self.addAttr(att, params.pop(att))
        self.internal.update(maker.internal)
        self.internal.update(params)
        self.tag = self.maker.tag
        self.add(data_stream)
        self.children.update(((k,maker.child_widget(c,self))\
                                for k, c in iteritems(maker.children)))
        
    def __repr__(self):
        if self.tag:
            return '<' + self.tag + self.flatatt() + '>'
        else:
            return '{0}({1})'.format(self.__class__.__name__,self.maker)
    __str__ = __repr__
    
    def __len__(self):
        return len(self.data_stream)
    
    def __iter__(self):
        return iter(self.data_stream)
    
    def content_type(self):
        return 'text/html'
    
    @property
    def parent(self):
        return self.internal.get('parent')
    
    @property
    def key(self):
        return self.maker.key
    
    @property
    def root(self):
        p = self.parent
        if p is not None:
            return p.root
        else:
            return self
    
    @property
    def data_stream(self):
        return self._data_stream
    
    def add(self, data_stream):
        '''Add to the stream. This functions delegates the adding to the
 :meth:`WidgetMaker.add_to_widget` method.'''
        if data_stream is not None:
            data_stream = iterable_for_widget(data_stream)
            for element in data_stream:
                self.maker.add_to_widget(self, element)
        return self
                
    def insert(self, position, element):
        self.maker.add_to_widget(self, element, position)
    
    def render(self, request=None, context=None):
        '''Render the widget. It accept two optional parameters, a http
request object and a dictionary for rendering children with a key.
        
:parameter request: Optional request object.
:parameter request: Optional context dictionary.
'''
        return async_object(StreamRenderer(self.stream(request, context)))
    
    def stream(self, request=None, context=None):
        '''Render the widget. It accept two optional parameters, a http
request object and a dictionary for rendering children with a key.
        
:parameter request: Optional request object.
:parameter request: Optional context dictionary.
'''
        if self._streamed:
            raise RuntimeError('{0} Already streamed'.format(self))
        self._streamed = True
        return self.maker.stream_from_widget(request, self, context)
    
    def hide(self):
        '''Set the ``css`` ``display`` property to ``none`` and return self
for concatenation.'''
        self.css({'display':'none'})
        return self
        
    def show(self):
        self.css.pop('display',None)
        return self
    

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
    
.. attribute:: inline

    If ``True`` the element is rendered as an inline element::
    
        <tag ....>
        
    rather than::
    
        <tag ...>
         ....
        </tag>
    
.. attribute:: children

    An ordered dictionary containing all :class:`WidgetMaker` instances
    which are direct children of the instance.
        
.. attribute:: widget_class

    The widget class used by the :meth:`widget` method when creating widgets.
    
    Default: :class:`Widget`
    
.. attribute:: default

    Optional string which register the ``self`` as the default maker for
    the value of ``default``. For Example::
    
        >>> from djpcms import html
        >>> html.WidgetMaker('div', default='div')
        >>> html.WidgetMaker('a', default='a.ajax')
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
    attributes = ('id', 'title', 'dir', 'style')
    default_attrs = None
    _widget = None
    _media = None
    
    def __init__(self, inline=None, default=False, description='', widget=None,
                 attributes=None, media=None, data=None, cn=None, key=None,
                 css=None, internal=None, **params):
        AttributeMixin.__init__(self, cn=cn, data=data, css=css)
        self.attributes = set(self.attributes)
        if attributes:
            self.attributes.update(attributes)
        self._media = media if media is not None else self._media
        self.description = description or self.description
        self.inline = inline if inline is not None else self.inline
        self.is_hidden = params.pop('is_hidden',self.is_hidden)
        self.tag = params.pop('tag', self.tag)
        if internal:
            self.internal.update(internal)
        self.key = key if key is not None else self.key
        self.default_style = params.pop('default_style', self.default_style)
        self._widget = widget or self._widget or Widget
        if self.default_attrs:
            p = self.default_attrs.copy()
            p.update(params)
            params = p
        for attr in self.attributes:
            if attr in params:
                value = params.pop(attr)
                attrp = 'process_{0}'.format(attr)
                if hasattr(self, attrp):
                    value = getattr(self, attrp)(value)
                self.addAttr(attr, value)
        # the remaining parameters are added to the data dictionary
        self.data.update(params)
        if not default and self.tag and self.tag not in default_widgets_makers:
            default = self.tag
        if default:
            default_widgets_makers[default] = self
    
    def __call__(self, data_stream=None, cn=None,
                 data=None, css=None, **params):
        # Create a Widget instance
        return self._widget(self, data_stream=data_stream, cn=cn, data=data,
                            css=css, **params)
        
    @property
    def widget_class(self):
        return self._widget
    
    @classmethod
    def makeattr(cls, *attrs):
        attr = set(attrs)
        attr.update(cls.attributes)
        return attr
    
    def __repr__(self):
        n =  '{0}{1}'.format(self.__class__.__name__,'-'+\
                             self.tag if self.tag else '')
        if self.key:
            n += '(' + self.key + ')'
        return n
    __str__ = __repr__
    
    def add(self, *widgets):
        '''Add children *widgets* to this class:`WidgetMaker`.
*widgets* must be class:`WidgetMaker`. It returns ``self`` for concatenation.'''
        for widget in widgets:
            if isinstance(widget, WidgetMaker):
                key = widget.key or len(self.children)
                self.children[key] = widget
                if not widget.default_style:
                    widget.default_style = self.default_style
                for k in self.internal:
                    if k not in widget.internal:
                        widget.internal[k] = self.internal[k]
        return self
  
    def add_to_widget(self, widget, element, position=None):
        '''Called by *widget* to add a new *element* to its data stream.
 By default it simply append *element* to the :attr:`Widget.data_stream`
 attribute. It can be overwritten but call super for consistency.'''
        if element is not None:
            if isinstance(element, Widget):
                element.internal['parent'] = widget
            if position is not None:
                widget._data_stream.insert(position, element)
            else:
                widget._data_stream.append(element)
                    
    def get_context(self, request, widget, context):
        '''Called by the :meth:`inner` method to build extra context.
By default it return *context*.'''
        return context
        
    def stream_from_widget(self, request, widget, context):
        '''Render the *widget* using the *context* dictionary and
information contained in this :class:`WidgetMaker`.'''
        if self.inline:
            if widget.tag:
                yield '<' + widget.tag + widget.flatatt() + '/>'
        else:
            context = self.get_context(request, widget, context)
            if widget.tag:
                yield '<' + widget.tag + widget.flatatt() + '>'
            for bit in self.stream(request, widget, context):
                yield bit
            if widget.tag:
                yield '</' + widget.tag + '>'
        if request:
            request.media.add(self.media(request, widget))
    
    def stream(self, request, widget, context):
        '''This method is called by :meth:`stream_from_widget` method.
It returns an iterable over chunks of html to be displayed in the
inner part of the widget.

:rtype: a generator of strings and :class:`ContextRenderer`.
'''
        if self.key and context and self.key in context:
            ctx = context.pop(self.key)
            if isinstance(ctx, dict):
                context = context.copy()
                context.update(ctx)
            else:
                widget.add(ctx)
        for child, data in zip_longest(widget.allchildren(),
                                       widget.data_stream):
            if child is not None:
                child.add(data)
                data = child
            if isinstance(data, Widget):
                for bit in data.stream(request, context):
                    yield bit
            else:
                yield data
            
    def child_widget(self, child_maker, widget, **params):
        '''Function invoked when there are children available. See the
:attr:`children`` attribute for more information on children.

:parameter child_maker: a :class:`WidgetMaker` child of self.
:parameter widget: The :class:`Widget` instance used for rendering.
:parameter kwargs: extra key-valued parameters to passed to the child
    widget constructor.
:rtype: An instance of :class:`Widget` for the child element.
'''
        p = {}
        p.update(widget.internal)
        p.update(params)
        p['parent'] = widget
        return child_maker(**p)
    
    def media(self, request, widget):
        return self._media


class Img(WidgetMaker):
    tag='img'
    inline=True
    attributes = WidgetMaker.makeattr('src', 'alt')


class Anchor(WidgetMaker):
    tag = 'a'
    attributes = WidgetMaker.makeattr('href', 'charset', 'name', 'rel', 'rev',
                                      'shape', 'target')
    
class Div(WidgetMaker):
    tag = 'div'
    
# set defaults
DefaultMaker = WidgetMaker()
Img()
Anchor()