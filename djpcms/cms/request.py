import sys
import re
import logging
import time
from inspect import isclass
from functools import partial 
from datetime import datetime, timedelta

# IMPORT PULSAR STUFF
from pulsar.apps.wsgi import WsgiResponse, WsgiHandler, WsgiResponseGenerator

from djpcms import media, is_renderer
from djpcms.cms import permissions
from djpcms.html import html_doc_stream
from djpcms.utils.decorators import lazyproperty, lazymethod
from djpcms.utils import orms
from djpcms.utils.async import is_async, is_failure, async_object, as_failure
from djpcms.utils.text import UnicodeMixin
from djpcms.utils.httpurl import parse_cookie, BytesIO, urljoin,\
                                 MultiValueDict, QueryDict, is_string,\
                                 itervalues, ispy3k, native_str, to_bytes,\
                                 iri_to_uri, parse_form_data,\
                                 has_empty_content

from .tree import DjpcmsTree, BadNode
from .exceptions import *

absolute_http_url_re = re.compile(r"^https?://", re.I)


__all__ = ['Response', 'is_xhr']


def is_xhr(environ):
    return environ.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

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
    def __init__(self, environ, node, instance, url, exc_info=None):
        self.environ = environ
        self.node = node
        if self.node is not None:
            self.view = node.view
        self.instance = instance
        self.url = url
        self.exc_info = exc_info
        
    def __getitem__(self, key):
        return self.environ[key]
    
    def __setitem__(self, key, value):
        self.environ[key] = value
        
    def get(self, key, default = None):
        return self.environ.get(key,default)
    
    @property
    def valid(self):
        return not bool(self.exc_info)
    
    @property
    def urlargs(self):
        return self.node.urlargs
    
    @property
    def settings(self):
        return self.view.settings
    
    @property
    def page(self):
        if self.view.inherit_page:
            node = self.node
            page = None
            while not page and node:
                page = node.page
                node = node.parent
            return page
        else:
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
        super(RequestNode,self).__init__(environ, node, instance, path)
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
            m = self.view.default_media(self)
            if m is None:
                m = media.Media(settings=self.view.settings)
            self._media = m
        return self._media
    
    @property
    def on_document_ready(self):
        return self.environ['on_document_ready']
    

def make_request(environ, node, instance=None, cache=True):
    '''Internal method for creating a :class:`Request` instance.'''
    if not node.error:
        view = node.view
        model = view.model
        if isclass(model):
            if not isinstance(instance, model):
                try:
                    # get the instance of model if any
                    instance = view.instance_from_variables(environ,
                                                            node.urlargs)
                    if is_async(instance):
                        callback = partial(build_request, environ, node, cache)
                        return instance.addBoth(
                                partial(build_request, environ, node, cache))
                except Exception as e:
                    instance = as_failure(e)
        else:
            instance = None
    return build_request(environ, node, cache, instance)


def build_request(environ, node, cache, instance):
    exc_info=None
    if is_failure(instance):
        exc_info, instance = instance.trace, None
    if node.error:
        url = environ.get('PATH_INFO', '/')
    else:
        if instance:
            urlargs = node.view.variables_from_instance(instance)
            node.urlargs.update(urlargs)
        url = node.url()
    if 'DJPCMS' not in environ:
        if url is None:
            raise ValueError('Critical error in request')
        environ['DJPCMS'] = RequestNode(node, instance, url)
    
    if cache and url is not None:
        rn = environ['DJPCMS']
        request = rn.requests.get(url)
        if request is None:
            request = Request(environ, node, instance, url, exc_info)
            rn.requests[url] = request
        return request
    else:
        # if we are not caching, return a request regardless if it has
        # a valid url or not
        return Request(environ, node, instance, url, exc_info)
    
    
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
    route attribute (check :class:`djpcms.cms.Route` for more information).
    
.. attribute:: instance

    For some views, the variable part of the urls is used to retrieve an
    instance of a :class:`djpcms.viewsApplication.model`.
    in this case this attribute is that instance, otherwise it is ``None``.
    
.. _WSGI: http://www.wsgi.org/en/latest/index.html
'''
    def for_path(self, path=None, urlargs=None, instance=None, cache=True):
        '''Create a new :class:`Request` from a given *path*.'''
        path = path if path is not None else self.path
        request = self.cache['requests'].get(path)
        if request:
            return request
        instance = instance if instance is not None else self.instance
        urlargs = urlargs if urlargs is not None else self.urlargs
        node = self.tree.get(path, urlargs)
        if not node:
            try:
                node = self.tree.resolve(path)
            except Http404:
                return None
        return make_request(self.environ, node, instance, cache=cache)
    
    def for_model(self, model=None, all=False, root=False, name=None,
                  urlargs=None, instance=None):
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
        app = self.app_for_model(model, all=all, root=root)
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
        if self.url is not None:
            return self.url + ' (' + self.path + ')'
        elif self.node:
            return self.node.path + ' (' + self.path + ')'
        else:
            return self.path
    
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
        return is_xhr(self.environ)
    
    @property    
    def REQUEST(self):
        if 'REQUEST' not in self.cache:
            res = MultiValueDict(((k,v[:]) for k,v in self.POST.lists()))
            res.update(self.GET)
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
    
    @property
    def appmodel(self):
        return self.view.appmodel
    
    @lazyproperty
    def encoding(self):
        return self.view.encoding(self)
    
    @lazyproperty
    def content_type(self):
        return self.view.content_type(self)
    
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
        if hasattr(icon, '__call__'):
            icon = icon(self)
        return icon
        
    def has_permission(self, code=None, instance=None, **kwargs):
        view = self.view
        perm = view.permissions
        user = kwargs.pop('user',self.user)
        # if code is not provided we check if the page can be viewed
        if code is None:
            page = self.page
            if page and not perm.has(self, permissions.VIEW, page, user = user):
                return False
            return perm.has(self, view.PERM, self.instance, user=user)
        else:
            # Check permissions on a different entity
            return perm.has(self, code, obj=instance, user=user, **kwargs)
    
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
        if view.pagination:
            return view.pagination
        elif view.appmodel:
            return view.appmodel.pagination
    
    def app_for_model(self, model, all=False, root=False):
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
            if isinstance(request, Request):
                yield request
    
Response = WsgiResponse


class DjpcmsResponseGenerator(WsgiResponseGenerator):
    '''Asynchronous response generator invoked by the djpcms WSGI middleware'''
    def __init__(self, website, environ, start_response):
        self.website = website
        super(DjpcmsResponseGenerator, self).__init__(environ, start_response)
        
    @property
    def site(self):
        return self.website()
    
    def __iter__(self):
        #query = self.environ.get('QUERY_STRING','')
        #PK = self.site.settings.PROFILING_KEY
        #gen = self.generate()
        #if PK and PK in query:
        #    profiler(self.generate)
        #    return profile_response(response)
        for request in self.request():
            if request is not None:
                break
            yield b''
        for response in self.response(request):
            if response is not None:
                break
            yield b''
        for c in self.start(response):
            yield c
    
    def response(self, request):
        '''Generate the Response'''
        self.content_type, response = request.content_type, None
        if not request.exc_info:           
            try:
                if request.method not in request.methods():
                    raise HttpException(status=405)
                elif not request.has_permission():
                    raise PermissionDenied()
                else:
                    content = request.view(request)
            except Exception as e:
                request.exc_info = sys.exc_info()
        if request.exc_info is None:
            content = self.safe_render(request, content)
            while is_async(content):
                yield
                content = self.safe_render(request, content)
            if is_failure(content):
                request.exc_info = content.trace
                content = b''
            elif isinstance(content, WsgiResponse):
                response = content
        # Response not yet available, build it from content or exc_info
        if response is None:
            response = Response(content_type=self.content_type,
                                encoding=request.encoding)
            if request.exc_info is not None:
                content = self.website.handle_error(request, response)
            if response.content_type == 'text/html' and not request.is_xhr:
                content = '\n'.join(html_doc_stream(request, content,
                                                    response.status_code))
            response.content = (to_bytes(content, response.encoding),)
        yield self.cache(request, response)
        
    def cache(self, request, response):
        '''Apply cache control headers of successful non ajax GET requests'''
        if request.method == 'get' and response.status_code == 200 and\
                not request.is_xhr:
            cache_control = request.view.get_cache_control()
            if cache_control:
                cache_control(response.headers)
        return response
        
    def request(self):
        tree, node, request, exc_info = None, None, None, None
        try:
            tree = self.page_tree()
            node = tree.resolve(self.environ['PATH_INFO'])
            request = make_request(self.environ, node)
        except Exception as e:
            exc_info = sys.exc_info()
        else:
            request = async_object(request)
            while is_async(request):
                yield
                request = async_object(request)    
            if is_failure(request):
                exc_info = request.trace
                request = None
        if request is None:
            if node is None:
                match = getattr(exc_info[1], 'handler', None)
                handler = self.site if match is None else match.handler()
                node = BadNode(tree, handler)
            request = make_request(self.environ, node)
            request.exc_info = exc_info
        for processor in self.site.request_processors:
            try:
                processor(request)
            except:
                pass
        yield request
        
    def page_tree(self):
        site = self.site
        Page = site.Page
        tree = site.tree
        if Page:
            return DjpcmsTree(tree, Page.query())
        else:
            return DjpcmsTree(tree)
        
    def safe_render(self, request, content):
        content = async_object(content)
        try:
            if is_renderer(content):
                self.content_type = content.content_type()
                content = async_object(content.render(request))
            return content
        except Exception as e:
            return as_failure(e)
