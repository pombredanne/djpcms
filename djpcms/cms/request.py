import sys
import re
import logging
import time
from inspect import isclass
from functools import partial
from datetime import datetime, timedelta

# IMPORT PULSAR STUFF
from pulsar.apps.wsgi import WsgiRequest, WsgiResponse, WsgiHandler
from pulsar.utils.structures import AttributeDictionary
from pulsar.utils.log import lazyproperty, lazymethod

from djpcms import media, is_renderer
from djpcms.cms import permissions
from djpcms.html import html_doc_stream
from djpcms.utils import orms
from djpcms.utils.httpurl import parse_cookie, BytesIO, urljoin,\
                                 MultiValueDict, QueryDict, is_string,\
                                 itervalues, ispy3k, native_str, to_bytes,\
                                 iri_to_uri, parse_form_data,\
                                 has_empty_content

from .tree import DjpcmsTree, BadNode
from .profiler import profile_generator
from .exceptions import *

absolute_http_url_re = re.compile(r"^https?://", re.I)


def get_request(environ, node=None):
    request = Request(environ, node=node)
    if request.cache.requests is None:
        request.cache.requests = {request.path: request}
    view = request.view
    if view and request.media is None:
        m = view.default_media(request)
        if m is None:
            m = media.Media(settings=view.settings)
        request.cache.media = m
    return request


def make_request(environ, node, instance=None, cache=True):
    '''Internal method for creating a :class:`Request` instance.'''
    instance = orms.orm_instance(instance)
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
    request_cache = environ.get('DJPCMS')
    if url is not None:
        requests = request_cache['REQUESTS']
        request = requests.get(url)
        if request is None:
            request = Request(environ, node, instance, url, exc_info)
            requests[url] = request
        else:
            request.update(node, instance, url, exc_info)
    else:
        # if we are not caching, return a request regardless if it has
        # a valid url or not
        request = Request(environ, node, instance, url, exc_info)
    return request


class Request(WsgiRequest):
    '''A wrapper for the WSGI_ *environ* dictionary.

.. attribute:: environ

    The WSGI environment dictionary

.. attribute:: view

    The :class:`ViewHandler` handler for this :class:`Request`.

.. attribute:: urlargs

    Dictionary of arguments from the variable part of the :attr:`view`
    route attribute (check :class:`Route` for more information).

.. attribute:: instance

    For :class:`djpcms.views.ObjectView` handlers, the variable part of the
    urls uniquely matches an instance of a
    :class:`djpcms.views.Application.model`. In this case this attribute
    is that instance, otherwise it is ``None``.

.. attribute:: page

    The page for this :class:`Request`. Only available if a valid Page model
    is available.

.. attribute:: closest_page

    Equivalent to :attr:`page` if available, otherwise the
    :attr:`page` of the closest ancestor with :attr:`page` available.
    This attribute is used for retrieving permission on a request. Check
    the :meth:`has_permission` method.

.. _WSGI: http://www.wsgi.org/en/latest/index.html
'''
    encoding = None
    page_editing = None

    def __init__(self, environ, node=None, instance=None, url=None,
                 exc_info=None):
        self.environ = environ
        if 'pulsar.cache' not in environ:
            environ['pulsar.cache'] = AttributeDictionary()
            self.cache.mixins = {}
        self.node = node
        self.instance = instance
        self.url = url
        self.exc_info = exc_info

    def __repr__(self):
        if self.cache.request == self:
            return self.path
        elif self.url is not None:
            return self.url + ' (' + self.path + ')'
        elif self.node:
            return self.node.path + ' (' + self.path + ')'
        else:
            return self.path
    __str__ = __repr__
    ###########################################################################
    #    environment shortcuts
    ###########################################################################
    @property
    def method(self):
        return self.environ.get('REQUEST_METHOD', 'get').lower()

    @property
    def REQUESTS(self):
        return self.cache['REQUESTS']

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
    def models(self):
        return self.cache.models

    @property
    def user(self):
        return self.cache.user

    @property
    def session(self):
        return self.cache.session

    def update(self, node, instance, url, exc_info):
        self.node = node
        self.instance = instance
        self.url = url
        self.exc_info = exc_info

    def for_path(self, path=None, urlargs=None, instance=None, cache=True):
        '''Create a new :class:`Request` from a given *path*. Additional
path key-valued parameters can be passed via the *urlargs* parameter.'''
        path = path if path is not None else self.path
        request = self.REQUESTS.get(path)
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
        return self.for_app(app, name, instance, urlargs)

    def for_app(self, app, name=None, instance=None, urlargs=None):
        if app:
            view = app.views.get(name) if name else None
            if not view and instance:
                view = app.view_for_instance(self, instance)
            view = view or app.root_view
            if view and not isinstance(view, self.__class__):
                view = self.for_path(view.path,
                                     urlargs=urlargs,
                                     instance=instance)
            return view

    ############################################################################
    #    DJPCMS shortcuts
    ############################################################################
    @property
    def view(self):
        if self.node:
            return self.node.view

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
    def name(self):
        return self.view.name

    @property
    def model(self):
        return getattr(self.view,'model',None)

    @property
    def tree(self):
        return self.node.tree

    @property
    def page(self):
        return self.node.page

    @lazyproperty
    def closest_page(self):
        node = self.node
        page = None
        while not page and node:
            page = node.page
            node = node.parent
        return page

    @property
    def appmodel(self):
        return self.view.appmodel

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
        return self.cache.media

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

    def has_permission(self, code=None, model=None, instance=None, **kwargs):
        return self.view.has_permission(self, code=code, model=model,
                                        instance=instance, **kwargs)

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
        '''Returns the HTTP host using the environment or request headers,
using the algorithm from PEP 3333.
SERVER_NAME combined with SCRIPT_NAME and PATH_INFO, can be used to
complete the URL. Note, however, that HTTP_HOST, if present, should be used
in preference to SERVER_NAME for reconstructing the request URL.
SERVER_NAME and SERVER_PORT can never be empty strings, and so are always
required.'''
        # We try three options, in order of decreasing preference.
        environ = self.environ
        if 'HTTP_X_FORWARDED_HOST' in environ:
            host = environ['HTTP_X_FORWARDED_HOST']
        elif 'HTTP_HOST' in environ:
            host = environ['HTTP_HOST']
        else:
            host = environ['SERVER_NAME']
            server_port = str(environ['SERVER_PORT'])
            if server_port != (self.is_secure and '443' or '80'):
                host = '%s:%s' % (host, server_port)
        return host

    def get_full_path(self, url=None):
        url = url or self.url
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
A shortcut for :meth:`ViewHandler.render`'''
        self.media.add(self.view.media(self))
        return self.view.render(self, **kwargs)

    def get_context(self, **kwargs):
        '''Proxy of :meth:`ViewHandler.get_context`, it return
 a context dictionary for the view'''
        return self.view.get_context(self, **kwargs)

    @lazyproperty
    def parent(self):
        node = self.node.parent
        instance = self.view.parent_instance(self.instance)
        if instance != self.instance:
            return self.for_model(instance=instance)
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
            if isinstance(model, str):
                return site.for_hash(model, all=all)
            elif model is not None:
                return site.for_model(model, all=all)
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
