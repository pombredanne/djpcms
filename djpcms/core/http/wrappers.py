import sys
import re
import logging
import time
from datetime import datetime, timedelta
from wsgiref.headers import Headers

from py2py3 import itervalues, ispy3k, native_str, to_bytestring,\
                         is_string, UnicodeMixin

from djpcms.utils import lazyproperty, lazymethod
from djpcms.utils.structures import MultiValueDict
from djpcms.utils.urls import iri_to_uri
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
           'ResponseRedirect']


STATUS_CODE_TEXT = BaseHTTPRequestHandler.responses
UNKNOWN_STATUS_CODE = ('UNKNOWN STATUS CODE','')

absolute_http_url_re = re.compile(r"^https?://", re.I)


class noinstance:
    pass


class Tree(object):
    
    def __init__(self, pages = None):
        if pages:
            self.pages = dict(((p.url,p) for p in pages))
        else:
            self.pages = {}
                

class Request(UnicodeMixin):
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
    _encoding = None
    upload_handlers = []
    
    def __init__(self, environ, view, urlargs = None, instance = None):
        self.environ = environ
        self.view = view
        self.urlargs = urlargs if urlargs is not None else {}
        self.__instance = instance

    def for_view_args(self, view = None, urlargs = None, instance = None):
        if view is not None:
            return Request(self.environ,
                           view if view is not None else self.view,
                           urlargs,
                           instance)
    
    def for_view(self, view):
        return self.for_view_args(view, self.urlargs.copy(), self.__instance)
    
    def for_path(self):
        info = self.DJPCMS
        return Request(info.view,info.urlargs)
    
    def __unicode__(self):
        return self.path + ' - ' + self.view.route.rule
    
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
    def encoding(self):
        if not self._encoding:
            try:
                self._encoding = self.DJPCMS.site.settings.DEFAULT_CHARSET
            except:
                self._encoding = 'utf-8'
        return self._encoding
    
    ############################################################################
    #    DJPCMS cached helpers
    ############################################################################
        
    @property
    def DJPCMS(self):
        return self.environ['DJPCMS']
    
    @property
    def cache(self):
        return self.DJPCMS.environ
    
    @property
    def media(self):
        return self.DJPCMS.media
    
    @property
    def name(self):
        return self.view.name
    
    @lazyproperty
    def page(self):
        if 'tree' not in self.cache:
            Page = self.view.root.Page
            if Page:
                self.cache['tree'] = Tree(Page.all())
            else:
                self.cache['tree'] = Tree()
        tree = self.cache['tree']
        return tree.pages.get(self.view.path)
            
    @lazyproperty
    def url(self):
        if self.view is self.DJPCMS.view:
            return self.path
        else:
            try:
                return self.view.get_url(self.urlargs,
                                         instance = self.instance)
            except Http404:
                return None
            
    @property
    def instance(self):
        return self.instance_from_variables()
        
    def instance_from_variables(self):
        if self.__instance is None:
            try:
                e = self.view.instance_from_variables(self.urlargs)
            except Http404:
                self.__instance = noinstance
                raise
            e = e if e is not None else noinstance
            self.__instance = e
        else:
            e = self.__instance
        return None if e is noinstance else e
    
    @lazyproperty    
    def title(self):
        return self.view.title(self)
    
    @lazyproperty    
    def linkname(self):
        return self.view.linkname(self)
    
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
        
    def has_permission(self):
        return self.view.has_permission(self, self.page, self.instance)
    
    def _get_cookies(self):
        if not hasattr(self, '_cookies'):
            c = self.environ.get('HTTP_COOKIE', '')
            if not ispy3k:
                c = to_bytestring(c)
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
            if server_port != (self.is_secure() and '443' or '80'):
                host = '%s:%s' % (host, server_port)
        return host
    
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
        if '_row_post_data' not in self.cache:
            try:
                content_length = int(self.environ.get('CONTENT_LENGTH', 0))
            except (ValueError, TypeError):
                content_length = 0
            if content_length:
                data = self.environ['wsgi.input'].read(content_length)
            else:
                data = b''
            self.cache['_row_post_data'] = data
        return self.cache['_row_post_data']
    
    def get_full_path(self):
        # RFC 3986 requires query string arguments to be in the ASCII range.
        # Rather than crash if this doesn't happen, we encode defensively.
        return '%s%s' % (self.path, self.environ.get('QUERY_STRING', '') \
            and ('?' + iri_to_uri(self.environ.get('QUERY_STRING', ''))) or '')
    
    def build_absolute_uri(self, location=None):
        """
        Builds an absolute URI from the location and the variables available in
        this request. If no location is specified, the absolute URI is built on
        ``request.get_full_path()``.
        """
        if not location:
            location = self.get_full_path()
        if not absolute_http_url_re.match(location):
            current_uri = '%s://%s%s' % (self.is_secure() and 'https' or 'http',
                                         self.get_host(), self.path)
            location = urljoin(current_uri, location)
        return iri_to_uri(location)
    
    @lazymethod
    def children(self):
        return tuple((self.for_view(v) for v in self.view.children(self)))
    
    @lazymethod
    def auth_children(self):
        return tuple((c for c in self.children() if c.has_permission()))
    
    def render(self):
        '''\
Render the underlying view.
A shortcut for :meth:`djpcms.views.djpcmsview.render`'''
        self.media.add(self.view.media(self))
        return self.view.render(self)
    
    @lazyproperty
    def parent(self):
        view = self.view
        url = self.url[1:]
        if not url:
            return None
        if url.endswith('/'):
            url = url[:-1]
        if url:
            bits = url.split('/')
            resolve = view.root.resolve
            while bits:
                bits.pop()
                url = '/'.join(bits) + '/' if bits else ''
                try:
                    view,args = resolve(url)
                except Http404:
                    continue
                else:
                    return self.for_view_args(view,args)
    
    @lazyproperty
    def in_navigation(self):
        return self.view.in_navigation(self)
    
    @property
    def pagination(self):
        return self.view.pagination or self.view.appmodel.pagination
    
    def viewurl(self, name = None, instance = None):
        '''retrieve a view url within this application.'''
        appmodel = self.view.appmodel
        if appmodel:
            return appmodel.viewurl(self, name = name, instance = instance)
    
    def for_model(self, model, all = False):
        model = native_str(model)
        if isinstance(model,str):
            apps = self.view.site.for_hash(model, all = all)
        elif model is not None:
            apps = self.view.site.for_model(model,all = all)
        else:
            return None
        if apps:
            return apps[0] if all else apps
        
    def view_for_model(self, model, all = False, name = None):
        '''return an :class:`Request` instance for a model view.'''
        app = self.for_model(model, all)
        if app:
            if name:
                return self.for_view(app.views.get(name))
            else:
                return self.for_view(app.root_view)
     
    
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
        elif isinstance(content,bytes):
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


