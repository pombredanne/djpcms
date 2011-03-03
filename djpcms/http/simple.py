'''Used for testing purposes only'''
import sys
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler

from djpcms import sites
from .utils import parse_cookie    


class HttpException(Exception):
    status = 500
    def __init__(self, msg = '', status = None):
        self.status = status or self.status
        super(HttpException,self).__init__(msg)
        
        
class Http404(HttpException):
    status = 404
    

def serve(port = 0, use_reloader = False):
    """Create a new WSGI server listening on `host` and `port` for `app`"""
    server = WSGIServer(('', port), WSGIRequestHandler)
    server.set_app(sites.wsgi)
    server.serve_forever()
    

class Request(object):
    '''Simple WSGI Request class'''
    def __init__(self, environ):
        self.environ = environ
        self.path = environ.get('PATH_INFO', '/')
        self.method = environ['REQUEST_METHOD'].upper()
        self.is_xhr = environ.get('HTTP_X_REQUESTED_WITH',None) == 'XMLHttpRequest'
        self._post_parse_error = False
        self._stream = self.environ['wsgi.input']
        self._read_started = False
        if self.method == 'POST':
            self.data_dict = dict(self.POST.items())
        else:
            self.data_dict = {}

    def get_full_path(self):
        # RFC 3986 requires query string arguments to be in the ASCII range.
        # Rather than crash if this doesn't happen, we encode defensively.
        return '%s%s' % (self.path, self.environ.get('QUERY_STRING', '') and ('?' + iri_to_uri(self.environ.get('QUERY_STRING', ''))) or '')

    def is_secure(self):
        return 'wsgi.url_scheme' in self.environ \
            and self.environ['wsgi.url_scheme'] == 'https'

    def _get_request(self):
        if not hasattr(self, '_request'):
            self._request = datastructures.MergeDict(self.POST, self.GET)
        return self._request

    def _get_get(self):
        if not hasattr(self, '_get'):
            # The WSGI spec says 'QUERY_STRING' may be absent.
            self._get = http.QueryDict(self.environ.get('QUERY_STRING', ''), encoding=self._encoding)
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
    
    
make_request = Request



class HttpResponse(object):
    mimetype = 'text/plain'
    status = 200
    
    def __init__(self, content, mimetype = None, status = None):
        self.content = content
        self.mimetype = mimetype or self.mimetype
        self.status = status or self.status
        self.headers = []
        
    def set_cookie(self, key, value='', max_age=None, expires=None,
                   path='/', domain=None, secure=None, httponly=False):
        """Sets a cookie. The parameters are the same as in the cookie `Morsel`
        object in the Python standard library but it accepts unicode data, too.

        :param key: the key (name) of the cookie to be set.
        :param value: the value of the cookie.
        :param max_age: should be a number of seconds, or `None` (default) if
                        the cookie should last only as long as the client's
                        browser session.
        :param expires: should be a `datetime` object or UNIX timestamp.
        :param domain: if you want to set a cross-domain cookie.  For example,
                       ``domain=".example.com"`` will set a cookie that is
                       readable by the domain ``www.example.com``,
                       ``foo.example.com`` etc.  Otherwise, a cookie will only
                       be readable by the domain that set it.
        :param path: limits the cookie to a given path, per default it will
                     span the whole domain.
        """
        self.headers.add('Set-Cookie', dump_cookie(key, value, max_age,
                         expires, path, domain, secure, httponly,
                         self.charset))

    def delete_cookie(self, key, path='/', domain=None):
        """Delete a cookie.  Fails silently if key doesn't exist.

        :param key: the key (name) of the cookie to be deleted.
        :param path: if the cookie that should be deleted was limited to a
                     path, the path has to be defined here.
        :param domain: if the cookie that should be deleted was limited to a
                       domain, that domain has to be defined here.
        """
        self.set_cookie(key, expires=0, max_age=0, path=path, domain=domain)
        
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
            len(self.response)
        except TypeError:
            return True
        return False