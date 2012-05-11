'''HTTP utilities and client library.
This is a thin layer on top of urllib2 in python2 / urllib in Python 3.
'''
import sys
import string

ispy3k = sys.version_info >= (3,0)

if ispy3k: # Python 3
    from urllib import request as urllibr
    from urllib.parse import quote, unquote, urlencode, urlparse, urlsplit
    from http.client import responses
    from http.cookiejar import CookieJar
    from http.cookies import SimpleCookie
    
    getproxies_environment = urllibr.getproxies_environment
    ascii_letters = string.ascii_letters
    iteritems = lambda d : d.items()

    def to_bytes(s, encoding=None, errors='strict'):
        encoding = encoding or 'utf-8'
        if isinstance(s, bytes):
            if encoding != 'utf-8':
                return s.decode('utf-8', errors).encode(encoding, errors)
            else:
                return s
        else:
            return ('%s'%s).encode(encoding, errors)
        
    def native_str(s):
        if isinstance(s, bytes):
            return s.decode('utf-8')
        else:
            return s
        
    def force_native_str(s):
        if isinstance(s, bytes):
            return s.decode('utf-8')
        else:
            return '%s' % s
        
else:   # pragma : no cover
    import urllib2 as urllibr
    from urllib import quote, unquote, urlencode, getproxies_environment
    from urlparse import urlparse, urlsplit
    from httplib import responses
    from cookielib import CookieJar
    from Cookie import SimpleCookie
    
    ascii_letters = string.letters
    
    range = xrange
    
    iteritems = lambda d : d.iteritems()
    
    def to_bytes(s, encoding=None, errors='strict'):
        encoding = encoding or 'utf-8'
        if isinstance(s, bytes):
            if encoding != 'utf-8':
                return s.decode('utf-8', errors).encode(encoding, errors)
            else:
                return s
        else:
            return unicode(value).encode(encoding, errors)
    
    def native_str(s):
        if isinstance(s, unicode):
            return s.encode('utf-8')
        else:
            return s
        
    def force_native_str(s):
        if isinstance(s, unicode):
            return s.encode('utf-8')
        else:
            return '%s' % s
    
    
escape = lambda s: quote(s, safe='~')

# The reserved URI characters (RFC 3986 - section 2.2)
URI_GEN_DELIMS = frozenset(':/?#[]@')
URI_SUB_DELIMS = frozenset("!$&'()*+,;=")
URI_RESERVED_SET = URI_GEN_DELIMS.union(URI_SUB_DELIMS)
URI_RESERVED_CHARS = ''.join(URI_RESERVED_SET)
# The unreserved URI characters (RFC 3986 - section 2.3)
URI_UNRESERVED_SET = frozenset(ascii_letters + string.digits + '-._~')

urlquote = lambda iri: quote(iri, safe=URI_RESERVED_CHARS)

def unquote_unreserved(uri):
    """Un-escape any percent-escape sequences in a URI that are unreserved
characters. This leaves all reserved, illegal and non-ASCII bytes encoded."""
    unreserved_set = UNRESERVED_SET
    parts = uri.split('%')
    for i in range(1, len(parts)):
        h = parts[i][0:2]
        if len(h) == 2:
            c = chr(int(h, 16))
            if c in unreserved_set:
                parts[i] = c + parts[i][2:]
            else:
                parts[i] = '%' + parts[i]
        else:
            parts[i] = '%' + parts[i]
    return ''.join(parts)

def iri_to_uri(iri, kwargs=None):
    '''Convert an Internationalized Resource Identifier (IRI) portion to a URI
portion that is suitable for inclusion in a URL.
This is the algorithm from section 3.1 of RFC 3987.
Returns an ASCII native string containing the encoded result.'''
    if iri is None:
        return iri
    iri = force_native_str(iri)
    if kwargs:
        iri = '%s?%s'%(iri,'&'.join(('%s=%s' % kv for kv in iteritems(kwargs))))
    return urlquote(unquote_unreserved(uri))


####################################################    HTTP CLIENT

class HttpClientResponse(object):
    '''Instances of this class are returned from the
:meth:`HttpClientHandler.request` method.

.. attribute:: status_code

    Numeric `status code`_ of the response
    
.. attribute:: url

    Url of request
    
.. attribute:: response

    Status code description
    
.. attribute:: headers

    List of response headers
    
.. attribute:: content

    Body of response
    
.. attribute:: is_error

    Boolean indicating if this is a response error.
    
.. _`status code`: http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
'''
    _resp = None
    status_code = None
    url = None
    HTTPError = urllibr.HTTPError
    URLError = urllibr.URLError 
    
    def __str__(self):
        if self.status_code:
            return '{0} {1}'.format(self.status_code,self.response)
        else:
            return '<None>'
    
    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__,self)
    
    @property
    def is_error(self):
        return isinstance(self._resp,Exception)
    
    @property
    def response(self):
        if self.status_code:
            return responses.get(self.status_code)
        
    def raise_for_status(self):
        """Raises stored :class:`HTTPError` or :class:`URLError`,
 if one occured."""
        if self.is_error:
            raise self._resp
    
    
class Response(HttpClientResponse):
    status_code = None
    
    def __init__(self, response):
        self._resp = response
        self.status_code = getattr(response, 'code', None)
        self.url = getattr(response, 'url', None)
    
    @property
    def headers(self):
        return getattr(self._resp,'headers',None)
    
    @property
    def content(self):
        if not hasattr(self,'_content') and self._resp:
            if hasattr(self._resp,'read'):
                self._content = self._resp.read()
            else:
                self._content = b''
        return getattr(self,'_content',None)
    
    def content_string(self):
        return self.content.decode()
    

class HttpClientHandler(object):
    '''Http client handler.'''
    HTTPError = urllibr.HTTPError
    URLError = urllibr.URLError
    DEFAULT_HEADERS = [('Connection', 'Keep-Alive')]
    
    def __init__(self, headers=None):
        dheaders = dict(self.DEFAULT_HEADERS)
        if headers:
            dheaders.update(headers)
        self.DEFAULT_HEADERS = dheaders
        
    def get_headers(self, headers):
        d = self.DEFAULT_HEADERS.copy()
        if headers:
            d.extend(headers)
        return d
    
    def request(self, url, method=None, **kwargs):
        '''Constructs and sends a request.

:param url: URL for the request.
:param method: request method, GET, POST, PUT, DELETE.
:param params: (optional) Dictionary or bytes to be sent in the query string for the :class:`Request`.
:param data: (optional) Dictionary or bytes to send in the body of the :class:`Request`.
:param headers: (optional) Dictionary of HTTP Headers to send with the :class:`Request`.
:param cookies: (optional) Dict or CookieJar object to send with the :class:`Request`.
:param files: (optional) Dictionary of 'filename': file-like-objects for multipart encoding upload.
:param auth: (optional) AuthObject to enable Basic HTTP Auth.
:param timeout: (optional) Float describing the timeout of the request.
:param allow_redirects: (optional) Boolean. Set to True if POST/PUT/DELETE redirect following is allowed.
:param proxies: (optional) Dictionary mapping protocol to the URL of the proxy.
:param return_response: (optional) If False, an un-sent Request object will returned.
:return: :class:`HttpClientResponse` object.
'''
        raise NotImplementedError
        
    def get(self, url):
        '''Sends a GET request and returns a :class:`HttpClientResponse`
object.'''
        return self.request(url, method = 'GET')
    
    def post(self, url, body = None):
        return self.request(url, body = body, method = 'POST')
    
    
class HttpClient(HttpClientHandler):
    '''Http handler from the standard library'''
    type = 1
    def __init__(self, proxy_info = None,
                 timeout = None, cache = None,
                 headers = None, handle_cookie = False):
        handlers = [ProxyHandler(proxy_info)]
        if handle_cookie:
            cj = CookieJar()
            handlers.append(HTTPCookieProcessor(cj))
        self._opener = build_opener(*handlers)
        self._opener.addheaders = self.get_headers(headers)    
        self.timeout = timeout
        
    @property
    def headers(self):
        return self._opener.addheaders
    
    def request(self, url, body=None, method=None, **kwargs):
        if isinstance(body, dict):
            method = method.upper() if method else 'POST'
            if method == 'POST':
                body = '&'.join(('%s=%s' % (escape(k),escape(v))\
                                        for k,v in iteritems(body)))
            else:
                url = iri_to_uri(url, **body)
                body = None
        else:
            body = to_bytes(body)
        try:
            req = Request(url, body, dict(self.headers))
            response = self._opener.open(req,timeout=self.timeout)
        except (HTTPError,URLError) as why:
            return Response(why)
        else:
            return Response(response)
    
    def add_password(self, username, password, uri, realm=None):
        '''Add Basic HTTP Authentication to the opener'''
        if realm is None:
            password_mgr = HTTPPasswordMgrWithDefaultRealm()
        else:
            password_mgr = HTTPPasswordMgr()
        password_mgr.add_password(realm, uri, user, passwd)
        self._opener.add_handler(HTTPBasicAuthHandler(password_mgr))
