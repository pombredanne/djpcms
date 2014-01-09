'''Introduces several utility classes for handling JSON AJAX
interaction with ``djpcms.js``
'''
import json

from pulsar import multi_async, maybe_async
from pulsar.utils.pep import to_string, string_type
from pulsar.utils.structures import OrderedDict

from djpcms import Renderer


def dorender(request, elem):
    if isinstance(elem, Renderer):
        elem=elem.render(request)
    return elem


ajax_json_types=('application/json', 'application/javascript')
ajax_content_types=ajax_json_types +\
                    ('text/javascript', 'text/plain', 'text/css')

class Ajax(Renderer):
    '''Base class for JSON AJAX utilities'''
    js = None
    _content_type=None
    _default_content_type='application/json'

    def __new__(cls, environ, *args, **kwargs):
        o=super(Ajax, cls).__new__(cls)
        if environ:
            contents = accept_content_type(environ.get('HTTP_ACCEPT'))
            if cls._default_content_type in contents:
                o._content_type=cls._default_content_type
            else:
                for c in ajax_content_types:
                    if c in contents:
                         o._content_type=c
                         break
                if not o._content_type:
                    raise ValueError('Could not set content type')
        return o

    def content_type(self):
        return self._content_type

    def serialize(self, request):
        '''This is the only functions that needs to be implemented by derived
classes. It converts ``self`` into a dictionary ready to be serialised
as JSON string.
        '''
        raise NotImplementedError()

    def dump(self, elem):
        if self.content_type() in ajax_json_types:
            return json.dumps(elem)
        else:
            return elem

    def render(self, request=None, **kwargs):
        '''Serialize ``self`` as a ``JSON`` string'''
        elem = maybe_async(self.serialize(request))
        if is_async(elem):
            return elem.add_callback(self.dump)
        else:
            return self.dump(elem)

    def error(self):
        return False

    def javascript(self, js):
        self.js = js


class Text(Ajax):
    def __init__(self, environ, text):
        self.text=text

    def serialize(self, request):
        elem=self.text
        if isinstance(elem, Renderer):
            elem=elem.render(request)
        return elem


class HeaderBody(Ajax):
    '''Base class for interacting with ``$.djpcms.jsonCallBack`` in
``djpcms.js``.
    '''
    def serialize(self, request):
        return multi_async(self._dict(
                    self.header(request), self.body(request)),
                    handle_value=lambda elem: dorender(request, elem))

    def header(self, request):
        '''Type of element recognized by ``$.djpcms.jsonCallBack``'''
        return ''

    def body(self, request):
        return ''

    def _dict(self, hd, bd):
        return {'header': hd,
                'body':   bd,
                'error':  self.error()}

    def handleError(self, e):
        js=self._dump(self._dict('server-error', e))
        return mark_safe(force_str(js))


class CustomHeaderBody(HeaderBody):

    def __init__(self, environ, h, b):
        self.h=h
        self.b=b

    def header(self, request):
        return self.h

    def body(self, request):
        return self.b


class jempty(HeaderBody):

    def header(self, request):
        return 'empty'


class message(CustomHeaderBody):

    def __init__(self, environ, text):
        super(message, self).__init__(environ, 'message', text)


class jservererror(CustomHeaderBody):

    def __init__(self, environ, text):
        super(jservererror, self).__init__(environ,
                                           'servererror', text)


class jerror(CustomHeaderBody):

    def __init__(self, environ, msg):
        super(jerror, self).__init__(environ, 'error', msg)


class jcollection(HeaderBody):
    '''A collection of HeaderBody elements'''
    def __init__(self, environ):
        self.data=[]

    def header(self, request):
        return 'collection'

    def add(self, elem):
        if isinstance(elem,HeaderBody):
            self.data.append(elem)

    def body(self, request):
        return [d.serialize(request) for d in self.data]


class jhtmls(HeaderBody):
    '''Contains a list of objects
        {identifier, html and type}

:parameter html: html to add to web page.
:parameter identifier: jquery selector
:parameter type: one of ``"replacewith"``, ``"replace"``, ``"addto"``.
    '''
    def __init__(self, environ, html=None, identifier=None, alldocument=True,
                 type='replace', removable=False):
        self.html=OrderedDict()
        if html != None:
            self.add(identifier, html, type, alldocument, removable)

    def header(self, request):
        return 'htmls'

    def __update(self, obj):
        html=self.html
        key =obj.get('identifier')
        objr=html.get(key,None)
        if objr is None:
            html[key]=obj
        else:
            objr['html'] += obj['html']

    def add(self, identifier, html='', type='replace',
            alldocument=True, removable=False):
        obj={'identifier': identifier,
               'html': html,
               'type': type,
               'alldocument': alldocument,
               'removable': removable}
        self.__update(obj)

    def update(self, html):
        if isinstance(html, jhtmls):
            html=html.html
        for v in html.values():
            self.__update(v)

    def body(self, request):
        return list(self.html.values())


class jattribute(HeaderBody):
    '''Modify ``dom`` attributes'''
    def __init__(self, environ):
        self.data=[]

    def header(self, request):
        return 'attribute'

    def body(self, request):
        return self.data

    def add(self, selector, attribute, value, alldocument=True):
        '''Add a new attribute to modify:

        :parameter selector: jQuery selector for the element to modify.
        :parameter attribute: attribute name (``id``, ``name``, ``href``, ``action`` ex.).
        :parameter value: new value for attribute.
        :parameter selector: ``True`` if selector to be applied to al document.'''
        self.data.append({'selector':selector,
                          'attr':attribute,
                          'value':value,
                          'alldocument':alldocument})


class jclass(HeaderBody):
    '''Modify, delete or add a new class to a dom element.'''
    def __init__(self, environ, selector, clsname, type='add'):
        self.selector=selector
        self.clsname=clsname
        self.type=type

    def header(self, request):
        return 'class'

    def body(self, request):
        return {'selector':self.selector,
                'clsname':self.clsname,
                'type':self.type}


class jerrors(jhtmls):

    def __init__(self, environ, **kwargs):
        super(jerrors, self).__init__(environ, **kwargs)

    def error(self):
        return True


class jremove(HeaderBody):

    def __init__(self, environ, identifier, alldocument=True):
        self.identifiers=[]
        self.add(identifier, alldocument)

    def add(self, identifier, alldocument=True):
        self.identifiers.append({'identifier': identifier,
                                 'alldocument': alldocument})

    def header(self, request):
        return 'remove'

    def body(self, request):
        return self.identifiers


class jredirect(HeaderBody):
    '''Redirect to new url'''
    def __init__(self, environ, url):
        self.url=url

    def header(self, request):
        return 'redirect'

    def body(self, request):
        return self.url


class jpopup(jredirect):
    '''Contains a link to use for opening a popup windows'''

    def header(self, request):
        return 'popup'


class dialog(HeaderBody):
    '''
    jQuery UI dialog
    '''
    def __init__(self, environ, hd='', bd=None, **kwargs):
        self.bd        =bd
        self.options   =self.get_options(hd,**kwargs)
        self.buttons   =[]

    def get_options(self, hd, **kwargs):
        return {'modal': kwargs.get('modal',False),
                'draggable': kwargs.get('draggable',True),
                'resizable': kwargs.get('resizable',True),
                'height':    kwargs.get('height','auto'),
                'width':     kwargs.get('width',300),
                'title':     hd,
                'dialogClass': kwargs.get('dialogClass','')}

    def header(self, request):
        return 'dialog'

    def body(self, request):
        return {'html':self.bd,
                'options':self.options,
                'buttons':self.buttons}

    def addbutton(self, name, url=None, func=None, close=True):
        self.buttons.append({'name':name,
                             'url':url,
                             'func':func,
                             'close':close})
