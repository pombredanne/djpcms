import sys
import re
import logging
import time
from datetime import datetime, timedelta
from wsgiref.headers import Headers

from py2py3 import itervalues, ispy3k, to_bytestring, is_string

from djpcms.utils import lazyproperty
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


class Request(object):
    '''WSGI Request class'''
    _encoding = None
    upload_handlers = []
    
    def __init__(self, environ, view = None, urlargs = None):
        self.environ = environ
        self.view = view
        self.urlargs = urlargs

    def for_view(self, view, **urlargs):
        return Request(self.environ, view, urlargs)
     
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
    
    @property
    def DJPCMS(self):
        return self.environ.get('DJPCMS')
    
    @lazyproperty
    def page(self):
        Page = self.view.root.Page
        if Page:
            return Page.get(self.view.path)
        
    @lazyproperty
    def instance(self):
        return None
    
    @lazyproperty    
    def title(self):
        return self.view.title(self)
    
    @lazyproperty
    def template_file(self):
        page = self.page
        # First Check if page has a template
        if page and page.template:
            return page.template
        view = self.view
        t = view.template_name
        if not t and view.appmodel:
            t = view.appmodel.template_name
        de = view.settings.DEFAULT_TEMPLATE_NAME
        if t:
            if de not in t:
                t += de
            return t
        else:
            return de
        
    def has_permission(self):
        return self.view.has_permission(self, self.page, self.instance)
        
    def _get_request(self):
        if not hasattr(self, '_request'):
            res = MultiValueDict(((k,v[:]) for k,v in self.POST.lists()))
            for k,gl in self.GET.lists():
                if k in res:
                    res.getlist(k).extend(gl)
                else:
                    res.setlist(k,gl[:])
            self._request = res
        return self._request

    def _get_get(self):
        if not hasattr(self, '_get'):
            # The WSGI spec says 'QUERY_STRING' may be absent.
            self._get = QueryDict(self.environ.get('QUERY_STRING', ''),
                                  encoding=self.encoding)
        return self._get

    def _set_get(self, get):
        self._get = get

    def _get_post(self):
        if not hasattr(self, '_post'):
            self._load_post_and_files()
        return self._post

    def _set_post(self, post):
        self._post = post

    def _get_cookies(self):
        if not hasattr(self, '_cookies'):
            c = self.environ.get('HTTP_COOKIE', '')
            if not ispy3k:
                c = to_bytestring(c)
            self._cookies = parse_cookie(c)
        return self._cookies

    def _set_cookies(self, cookies):
        self._cookies = cookies

    def _get_files(self):
        if not hasattr(self, '_files'):
            self._load_post_and_files()
        return self._files

    GET = property(_get_get, _set_get)
    POST = property(_get_post, _set_post)
    COOKIES = property(_get_cookies, _set_cookies)
    FILES = property(_get_files)
    REQUEST = property(_get_request)
    
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
        if self.method != 'POST':
            self._post, self._files = QueryDict('', encoding=self.encoding),\
                                        MultiValueDict()
        elif self.environ.get('CONTENT_TYPE', '').startswith('multipart'):
            self._raw_post_data = ''
            self._post, self._files = parse_form_data(self.environ,
                                                      self.encoding)
        else:
            self._post, self._files = QueryDict(self.raw_post_data(),\
                                    encoding=self.encoding), MultiValueDict()
    
    def raw_post_data(self):
        if not hasattr(self, '_raw_post_data'):
            if self._read_started:
                raise Exception("You cannot access raw_post_data after reading\
 from request's data stream")
            try:
                content_length = int(self.environ.get('CONTENT_LENGTH', 0))
            except (ValueError, TypeError):
                content_length = 0
            if content_length:
                self._raw_post_data = self._stream.read(content_length)
            else:
                self._raw_post_data = b''
            #    self._raw_post_data = self._stream.read()
            self._stream = BytesIO(self._raw_post_data)
        return self._raw_post_data
    
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


