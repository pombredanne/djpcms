import sys
import re
import logging
import time
from datetime import datetime, timedelta

from py2py3 import itervalues,is_string,to_string, ispy3k

from djpcms.utils.structures import MultiValueDict
from djpcms.utils.urls import iri_to_uri
from djpcms.core.exceptions import *

from .utils import parse_cookie, BaseHTTPRequestHandler, parse_qsl, SimpleCookie,\
                   BytesIO, cookie_date, urljoin
from .multiparser import MultiPartParser


__all__ = ['STATUS_CODE_TEXT',
           'UNKNOWN_STATUS_CODE',
           'Request',
           'Response',
           'ResponseRedirect',
           'HttpException',
           'Http404',
           'path_with_query']


STATUS_CODE_TEXT = BaseHTTPRequestHandler.responses
UNKNOWN_STATUS_CODE = ('UNKNOWN STATUS CODE','')

absolute_http_url_re = re.compile(r"^https?://", re.I)


if ispy3k:
    def to_header_strings(*values):
        for value in values:
            if isinstance(value,bytes):
                value = value.decode()
            else:
                value = str(value)
            yield value
else:
    def to_header_strings(*values):
        for value in values:
            yield str(value)
    
    
def set_header(self, key, value):
    self.set_header(key, value)
    

def path_with_query(request):
    path = request.path
    if request.method == 'GET':
        qs =  request.environ['QUERY_STRING']
        if qs:
            return path + '?' + qs
    return path
    

class QueryDict(MultiValueDict):
    
    def __init__(self, query_string, encoding = None):
        super(QueryDict,self).__init__()
        self.encoding = encoding
        for key, value in parse_qsl((query_string or ''), True): # keep_blank_values=True
            self.appendlist(to_string(key, encoding, errors='replace'),
                            to_string(value, encoding, errors='replace'))
    

class Request(object):
    '''Simple WSGI Request class'''
    _encoding = None
    upload_handlers = []
    
    def __init__(self, environ):
        self.environ = environ
        self.path = environ.get('PATH_INFO', '/')
        self.method = environ['REQUEST_METHOD'].upper()
        self.is_xhr = environ.get('HTTP_X_REQUESTED_WITH',None) == 'XMLHttpRequest'
        self._post_parse_error = False
        self._stream = self.environ['wsgi.input']
        self._read_started = False

    def is_secure(self):
        return 'wsgi.url_scheme' in self.environ \
            and self.environ['wsgi.url_scheme'] == 'https'
    
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
        return self.environ.get('DJPCMS',None)
    
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
            self._get = QueryDict(self.environ.get('QUERY_STRING', ''), encoding=self.encoding)
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
            self._cookies = parse_cookie(self.environ.get('HTTP_COOKIE', ''))
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
            self._post, self._files = self.parse_file_upload(self.META, self)
        else:
            self._post, self._files = QueryDict(self.raw_post_data(),\
                                         encoding=self.encoding), MultiValueDict()

    def parse_file_upload(self, META, post_data):
        """Returns a tuple of (POST QueryDict, FILES MultiValueDict)."""
        upload_handlers = self.DJPCMS.upload_handlers()
        parser = MultiPartParser(META, post_data, upload_handlers, self.encoding)
        return parser.parse()
    
    def raw_post_data(self):
        if not hasattr(self, '_raw_post_data'):
            if self._read_started:
                raise Exception("You cannot access raw_post_data after reading from request's data stream")
            try:
                content_length = int(self.environ.get('CONTENT_LENGTH', 0))
            except (ValueError, TypeError):
                content_length = 0
            if content_length:
                self._raw_post_data = self._stream.read(content_length)
            else:
                self._raw_post_data = self._stream.read()
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
    
    def djp(self, view = None, **kwargs):
        info = self.DJPCMS
        if view is None:
            return info.djp(self)
        else:
            return view(self,**kwargs)
            
    

class Response(object):
    DEFAULT_CONTENT_TYPE = 'text/plain'
    status = 200
    
    def __init__(self, content = '', status = None, content_type = None, encoding = None):
        self.encoding = encoding
        if not content:
            content = ()
        if is_string(content):
            if encoding:
                content = content.encode(encoding)
            else:
                content = content.encode()
            content = bytes(content)
        if isinstance(content,bytes):
            content = (content,)
        self.content = content
        self.status = status or self.status
        self._headers = {}
        self.cookies = SimpleCookie()
        self.content_type = content_type or self.DEFAULT_CONTENT_TYPE
        self.set_header('Content-Type',content_type)
        if encoding:
            self.set_header("Content-Encoding", encoding)
    
    def __setitem__(self, header, value):
        self.set_header(header, value)
        
    def __getitem__(self, header):
        return self._headers[header.lower()]
        
    def set_header(self, header, value):
        header, value = to_header_strings(header.lower(), value)
        self._headers[header] = (header, value)

    def __contains__(self, header):
        """Case-insensitive check for a header."""
        return header.lower() in self._headers
    
    def __iter__(self):
        return iter(self.content)
        
    @property
    def status_code(self):
        return int(self.status)
    
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
        status_text = STATUS_CODE_TEXT.get(self.status,UNKNOWN_STATUS_CODE)[0]
        status = '%s %s' % (self.status, status_text)
        for c in self.cookies.values():
            self.set_header('Set-Cookie', c.output(header=''))
        if start_response is not None:
            start_response(status, list(itervalues(self._headers)))
        return self

    
class ResponseRedirect(Response):
    status_code = 302

    def __init__(self, redirect_to):
        super(ResponseRedirect, self).__init__()
        self['Location'] = iri_to_uri(redirect_to)

