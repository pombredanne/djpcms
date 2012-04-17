import sys
import re
import logging
import time
from inspect import isclass
from functools import partial 
from datetime import datetime, timedelta
from wsgiref.headers import Headers

import djpcms
from djpcms.utils.py2py3 import itervalues, ispy3k, native_str, to_bytes,\
                                is_string, UnicodeMixin
from djpcms.utils import lazyproperty, lazymethod, js, media
from djpcms.utils.structures import MultiValueDict
from djpcms.utils.urls import iri_to_uri
from djpcms.core import orms
from djpcms.core.exceptions import *

from .utils import parse_cookie, BaseHTTPRequestHandler,\
                   SimpleCookie, BytesIO, cookie_date, urljoin,\
                   MultiValueDict, QueryDict
from .multipart import parse_form_data


__all__ = ['STATUS_CODE_TEXT',
           'UNKNOWN_STATUS_CODE',
           'QueryDict',
           'setResponseClass',
           'Request',
           'Response',
           'ResponseRedirect',
           'save_on_cache',
           'save_on_request']


STATUS_CODE_TEXT = BaseHTTPRequestHandler.responses
UNKNOWN_STATUS_CODE = ('UNKNOWN STATUS CODE','')

absolute_http_url_re = re.compile(r"^https?://", re.I)


class noinstance:
    pass


def save_on_cache(f):
    name = getattr(f,'cache_key',f.__name__)
    def _(self,request):
        cache = request.cache
        if name not in cache:
            cache[name] = f(self,request) 
        return cache[name]
    return _


def save_on_request(f):
    name = '_cached_function_' + f.__name__
    def _(self,request):
        if not hasattr(request,name):
            setattr(request, name, f(self,request))
        return getattr(request,name)
    return _


class NodeEnvironMixin(UnicodeMixin):
    view = None
    page_editing = False
    def __init__(self, environ, node, instance, url):
        self.environ = environ
        self.node = node
        if self.node is not None:
            self.view = node.view
        self.instance = instance
        self.url = url
        
    def __getitem__(self, key):
        return self.environ[key]
    
    def __setitem__(self, key, value):
        self.environ[key] = value
        
    def get(self, key, default = None):
        return self.environ.get(key,default)
    
    @property
    def urlargs(self):
        return self.node.urlargs
    
    @property
    def settings(self):
        return self.view.settings
    
    @property
    def page(self):
        return self.node.page
    
    @property
    def name(self):
        return self.view.name
    
    @property
    def model(self):
        return getattr(self.view,'model',None)
    
    @property
    def tree(self):
        return self.node.tree
    
    
class RequestNode(NodeEnvironMixin):
    '''Holds information and data to be reused during a single request.
This is used as a way to speed up responses as well as for
managing settings.'''
    def __init__(self, node, instance, path):
        environ = {'requests':{},
                   'traces':[],
                   'on_document_ready':[]}
        super(RequestNode,self).__init__(environ,node,instance,path)
        self.path = path
        
    def __unicode__(self):
        return self.name
    
    @property
    def request(self):
        return self.requests.get(self.path)
    
    @property
    def requests(self):
        return self.environ['requests']
    
    @property
    def media(self):
        if not hasattr(self,'_media'):
            settings = self.view.settings
            m = media.Media(settings = settings)
            m.add_js(js.jquery_paths(settings))
            m.add_js(js.bootstrap(settings))
            m.add_js(settings.DEFAULT_JAVASCRIPT)
            m.add_css(settings.DEFAULT_STYLE_SHEET)
            m.add(self.view.media(self))
            self._media = m
        return self._media
    
    @property
    def on_document_ready(self):
        return self.environ['on_document_ready']
    

def make_request(environ, node, instance = None, cache = True, safe = True):
    if not node.error:
        view = node.view
        model = view.model
        if isclass(model):
            if not isinstance(instance, model):
                try:
                    instance = view.instance_from_variables(environ,
                                                            node.urlargs)
                    callback = partial(build_request, environ, node, cache)
                    return view.response(instance, callback)
                except:
                    if not safe:
                        raise
                    # set instance to None
                    instance = None
            if instance:
                urlargs = view.variables_from_instance(instance)
                node.urlargs.update(urlargs)
        else:
            instance = None
    
    return build_request(environ,node,cache,instance)


def build_request(environ, node, cache, instance):
    if node.error:
        url = environ.get('PATH_INFO', '/')
    else:
        url = node.url()
    if 'DJPCMS' not in environ:
        if url is None:
            raise ValueError('Critical error in request')
        environ['DJPCMS'] = RequestNode(node,instance,url)
    
    if cache:
        if url is not None:
            rn = environ['DJPCMS']
            request = rn.requests.get(url)
            if request is None:
                request = Request(environ, node, instance, url)
                rn.requests[url] = request
            return request
    else:
        # if we are not caching, return a request regarthless it has
        # a valid url or not
        return Request(environ, node, instance, url)
    
    
class Request(NodeEnvironMixin):
    '''A lightweight class which wraps the WSGI_ request environment, the
:class:`djpcms.views.djpcmsview` serving the request and the request
arguments.
 
.. attribute:: environ

    The WSGI environment dictionary
     
.. attribute:: view

    The request handler
    
.. attribute:: urlargs

    Dictionary of arguments from the variable part of the :attr:`view`
    route attribute (check :class:`djpcms.Route` for more information).
    
.. attribute:: instance

    For some views, the variable part of the urls is used to retrieve an
    instance of a :class:`djpcms.viewsApplication.model`.
    in this case this attribute is that instance, otherwise it is ``None``.
    
.. _WSGI: http://www.wsgi.org/en/latest/index.html
'''
    def for_path(self, path = None, urlargs = None, instance = None,
                 cache = True):
        '''Create a new :class:`Request` from a given *path*.'''
        path = path if path is not None else self.path
        request = self.cache['requests'].get(path)
        if request:
            return request
        instance = instance if instance is not None else self.instance
        urlargs = urlargs if urlargs is not None else self.urlargs
        node = self.tree.get(path,urlargs)
        if not node:
            try:
                node = self.tree.resolve(path)
            except Http404:
                return None
        return make_request(self.environ, node, instance, cache = cache)
    
    def for_model(self, model = None, all = False, root = False, name = None,
                  urlargs = None, instance = None):
        '''Create a new :class:`Request` instance for a model class. The
model can be specified directly or indirectly via the *instance* parameter.

:parameter model: model class to search.
:parameter model: all check all sites.
:parameter root: Start the search from the root site.
:parameter name: Optional view name if you require a non standard view
    (root view when instance is ``None`` or the
    :meth:`djpcms.views.Application.view_for_instance` result).
:parameter urlargs: url variables.
:parameter instance: optional instance of model.

If *instance* is provided, *model* is given by the instance class and therefore
overrides the *model* input. In addition if *name* is not given and *instance*
is available, the name is set to ``view``.
'''
        if instance is None:
            model = model or self.model
        else:
            mapper = orms.mapper(instance)
            if not mapper:
                return
            model = mapper.model
        app = self.app_for_model(model, all = all, root = root)
        if app:
            view = app.views.get(name) if name else None
            if not view and instance:
                view = app.view_for_instance(self, instance)
            view = view or app.root_view
            if view and not isinstance(view, self.__class__):
                view = self.for_path(view.path, urlargs = urlargs,
                                     instance = instance)
            return view
            
    def __unicode__(self):
        return self.url + ' (' + self.path + ')'
    
    ############################################################################
    #    environment shortcuts
    ############################################################################
    
    @property
    def is_secure(self):
        return 'wsgi.url_scheme' in self.environ \
            and self.environ['wsgi.url_scheme'] == 'https'
    
    @property
    def path(self):
        return self.environ.get('PATH_INFO', '/')
    
    @property
    def method(self):
        return self.environ.get('REQUEST_METHOD','get').lower()
    
    @property
    def is_xhr(self):
        return self.environ.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
    
    @property    
    def REQUEST(self):
        if 'REQUEST' not in self.cache:
            res = MultiValueDict(((k,v[:]) for k,v in self.POST.lists()))
            for k,gl in self.GET.lists():
                if k in res:
                    res.getlist(k).extend(gl)
                else:
                    res.setlist(k,gl[:])
            self.cache['REQUEST'] = res
        return self.cache['REQUEST']

    @property
    def GET(self):
        if 'GET' not in self.cache:
            self.cache['GET'] = QueryDict(self.environ.get('QUERY_STRING', ''),
                                          encoding=self.encoding)
        return self.cache['GET']

    @property
    def POST(self):
        if 'POST' not in self.cache:
            self._load_post_and_files()
        return self.cache['POST']

    @property
    def FILES(self):
        if 'FILES' not in self.cache:
            self._load_post_and_files()
        return self.cache['FILES']
    
    @property
    def user(self):
        return self.environ.get('user')
    
    @property
    def session(self):
        return self.environ.get('session')
    
    @property
    def DJPCMS(self):
        return self.environ['DJPCMS']
    
    @property
    def cache(self):
        return self.DJPCMS.environ
    
    ############################################################################
    #    View methods and properties
    ############################################################################
    
    @lazyproperty
    def encoding(self):
        return self.view.encoding(self)
    
    @lazymethod
    def underlying(self):
        return self.view.underlying(self)
    
    def methods(self):
        return self.view.methods(self)
    
    @property
    def media(self):
        return self.DJPCMS.media
    
    @property
    def on_document_ready(self):
        return self.DJPCMS.on_document_ready
        
    @lazyproperty    
    def title(self):
        return self.view.title(self)
    
    @lazyproperty    
    def linkname(self):
        return self.view.linkname(self)
    
    @lazyproperty
    def icon(self):
        icon = self.view.ICON
        if hasattr(icon,'__call__'):
            icon = icon(self)
        return icon
    
    @lazyproperty
    def template_file(self):
        page = self.page
        # First Check if page has a template
        if page and page.template:
            return page.template
        view = self.view
        t = view.template_file
        if not t and view.appmodel:
            t = view.appmodel.template_file
        de = view.settings.DEFAULT_TEMPLATE_NAME
        if t:
            if de not in t:
                t += de
            return t
        else:
            return de
        
    def render_to_response(self, context, **kwargs):
        return self.view.response.render_to_response(self, context, **kwargs)
        
    def has_permission(self, code = None, instance = None, **kwargs):
        view = self.view
        perm = view.permissions
        user = kwargs.pop('user',self.user)
        # if code is not provided we check if the page can be viewed
        if code is None:
            page = self.page
            if page and not perm.has(self, djpcms.VIEW, page, user = user):
                return False
            return perm.has(self, view.PERM, self.instance, user = user)
        else:
            # Check permissions on a different entity
            return perm.has(self, code, obj = instance, user = user, **kwargs)
    
    def _get_cookies(self):
        if not hasattr(self, '_cookies'):
            c = self.environ.get('HTTP_COOKIE', '')
            if not ispy3k:
                c = to_bytes(c)
            self._cookies = parse_cookie(c)
        return self._cookies

    def _set_cookies(self, cookies):
        self._cookies = cookies

    COOKIES = property(_get_cookies, _set_cookies)
    
    def get_host(self):
        """Returns the HTTP host using the environment or request headers."""
        # We try three options, in order of decreasing preference.
        environ = self.environ
        if 'HTTP_X_FORWARDED_HOST' in environ:
            host = environ['HTTP_X_FORWARDED_HOST']
        elif 'HTTP_HOST' in environ:
            host = environ['HTTP_HOST']
        else:
            # Reconstruct the host using the algorithm from PEP 333.
            host = environ['SERVER_NAME']
            server_port = str(environ['SERVER_PORT'])
            if server_port != (self.is_secure and '443' or '80'):
                host = '%s:%s' % (host, server_port)
        return host
    
    def get_full_path(self):
        url = self.url
        qs = self.environ.get('QUERY_STRING', '')
        if url == self.path and qs:
            return url + '?' + iri_to_uri(qs)
        else:
            return url
    
    def build_absolute_uri(self, location=None):
        """
        Builds an absolute URI from the location and the variables available in
        this request. If no location is specified, the absolute URI is built on
        ``request.get_full_path()``.
        """
        if not location:
            location = self.get_full_path()
        if not absolute_http_url_re.match(location):
            current_uri = '%s://%s%s' % (self.is_secure and 'https' or 'http',
                                         self.get_host(), self.path)
            location = urljoin(current_uri, location)
        return iri_to_uri(location)
    
    @lazymethod
    def cssgrid(self):
        grid = self.view.cssgrid(self)
        if grid:
            self.media.add(grid.media(self))
        return grid

    @lazymethod
    def children(self):
        return tuple(self._children())
    
    @lazymethod
    def auth_children(self):
        return tuple((c for c in self.children() if c.has_permission()))
    
    def render(self, **kwargs):
        '''\
Render the underlying view.
A shortcut for :meth:`djpcms.views.djpcmsview.render`'''
        self.media.add(self.view.media(self))
        return self.view.render(self, **kwargs)
    
    def get_context(self, **kwargs):
        '''Proxy of :meth:`djpcms.views.djpcmsview.get_context`, it return
 a context dictionary for the view'''
        return self.view.get_context(self, **kwargs)
    
    @lazyproperty
    def parent(self):
        node = self.node.parent
        instance = self.view.parent_instance(self.instance)
        if instance != self.instance:
            return self.for_model(instance = instance)
        elif node:
            return make_request(self.environ, node, instance)
    
    @lazyproperty
    def in_navigation(self):
        return self.view.in_navigation(self)
    
    @property
    def pagination(self):
        view = self.view
        if view:
            return view.pagination
        elif view.appmodel:
            return view.appmodel.pagination
    
    def app_for_model(self, model, all = False, root = False):
        '''Fetch an :class:`djpcms.views.Application` for a given *model*.

:parameter all: if ``True`` it returns a list of all matched applications,
    otherwise it return the first found.
:parameter root: if ``True`` the search will start from the root site,
    otherwise it starts from the current site.
    Defaulr: ``False``.
'''
        if model == self.model:
            return self.view.appmodel
        else:
            model = native_str(model)
            site = self.view.root if root else self.view.site 
            if isinstance(model,str):
                return site.for_hash(model, all = all)
            elif model is not None:
                return site.for_model(model, all = all)
            else:
                return None
        
    ############################################################################
    #    Private methods
    ############################################################################

    def _load_post_and_files(self):
        # Populates self._post and self._files
        if self.method != 'post':
            p,f = QueryDict('', encoding=self.encoding),MultiValueDict()
        elif self.environ.get('CONTENT_TYPE', '').startswith('multipart'):
            p,f = parse_form_data(self.environ, self.encoding)
        else:
            p,f = QueryDict(self._post_data(),encoding=self.encoding),\
                  MultiValueDict()
        self.cache['POST'] = p
        self.cache['FILES'] = f
    
    def _post_data(self):
        if 'raw_post_data' not in self.cache:
            try:
                content_length = int(self.environ.get('CONTENT_LENGTH', 0))
            except (ValueError, TypeError):
                content_length = 0
            if content_length:
                data = self.environ['wsgi.input'].read(content_length)
            else:
                data = b''
            self.cache['raw_post_data'] = data
        return self.cache['raw_post_data']
    
    def _children(self):
        instance = self.instance
        environ = self.environ
        for node in self.node.children():
            request = make_request(environ, node, instance)
            if request is not None:
                yield request
    
     
class Response_(object):
    '''A wrapper for response contents.
    
.. attribute:: content
    
    an iterable over contents
    
.. attribute:: status

    Integer indicating the response status code
    '''
    DEFAULT_CONTENT_TYPE = 'text/plain'
    status_code = 200
    
    def __init__(self, content = '', status = None, content_type = None,
                 response_headers = None, encoding = None):
        self.encoding = encoding
        if not content:
            content = ()
        elif isinstance(content, bytes):
            content = (content,)
        elif is_string(content):
            raise ValueError('Response cannot accept unicode.')
        self.content = content
        self.status_code = int(status or self.status_code)
        self.cookies = SimpleCookie()
        content_type = content_type or self.DEFAULT_CONTENT_TYPE
        self.headers = Headers(response_headers or [])
        self.headers['Content-type'] = content_type
    
    def __iter__(self):
        return iter(self.content)
        
    def set_cookie(self, key, value='', max_age=None, expires=None, path='/',
                   domain=None, secure=False, httponly=False):
        """
        Sets a cookie.

        ``expires`` can be a string in the correct format or a
        ``datetime.datetime`` object in UTC. If ``expires`` is a datetime
        object then ``max_age`` will be calculated.
        """
        self.cookies[key] = value
        if expires is not None:
            if isinstance(expires, datetime):
                delta = expires - expires.utcnow()
                # Add one second so the date matches exactly (a fraction of
                # time gets lost between converting to a timedelta and
                # then the date string).
                delta = delta + timedelta(seconds=1)
                # Just set max_age - the max_age logic will set expires.
                expires = None
                max_age = max(0, delta.days * 86400 + delta.seconds)
            else:
                self.cookies[key]['expires'] = expires
        if max_age is not None:
            self.cookies[key]['max-age'] = max_age
            # IE requires expires, so set it if hasn't been already.
            if not expires:
                self.cookies[key]['expires'] = cookie_date(time.time() +
                                                           max_age)
        if path is not None:
            self.cookies[key]['path'] = path
        if domain is not None:
            self.cookies[key]['domain'] = domain
        if secure:
            self.cookies[key]['secure'] = True
        if httponly:
            self.cookies[key]['httponly'] = True

    def delete_cookie(self, key, path='/', domain=None):
        self.set_cookie(key, max_age=0, path=path, domain=domain,
                        expires='Thu, 01-Jan-1970 00:00:00 GMT')
        
    @property
    def is_streamed(self):
        """If the response is streamed (the response is not an iterable with
        a length information) this property is `True`.  In this case streamed
        means that there is no information about the number of iterations.
        This is usually `True` if a generator is passed to the response object.

        This is useful for checking before applying some sort of post
        filtering that should not take place for streamed responses.
        """
        try:
            len(self.content)
        except TypeError:
            return True
        return False
    
    def __call__(self, environ, start_response):
        '''Close the response'''
        headers = self.headers
        status_text = STATUS_CODE_TEXT.get(self.status_code,
                                           UNKNOWN_STATUS_CODE)[0]
        status = '%s %s' % (self.status_code, status_text)

        for c in self.cookies.values():
            headers['Set-Cookie'] = c.OutputString()
        
        if "Content-Encoding" not in headers and self.encoding:
            headers["Content-Encoding"] = self.encoding
             
        if not self.is_streamed:
            cl = 0
            for x in self:
                cl += len(x)
            headers["Content-Length"] = str(cl)
            
        start_response(status, headers.items())    
        return self


ResponseClass = None


def setResponseClass(respcls):
    global ResponseClass
    ResponseClass = respcls


def Response(*args, **kwargs):
    if ResponseClass == None:
        return Response_(*args, **kwargs)
    else:
        return ResponseClass(*args, **kwargs)
        

def ResponseRedirect(redirect_to):
    return Response(status = 302,
            response_headers = [('Location', iri_to_uri(redirect_to))])


