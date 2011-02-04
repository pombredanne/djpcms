import sys
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler

from djpcms import sites


class HttpResponse(object):
    pass


def serve(port = 0, use_reloader = False):
    """Create a new WSGI server listening on `host` and `port` for `app`"""
    server = WSGIServer(('', port), WSGIRequestHandler)
    server.set_app(sites.wsgi)
    server.serve_forever()
    
    
def make_request(environ):
    return Request(environ)


class Request(object):
    '''Simple WSGI Request class'''
    def __init__(self, environ):
        script_name = self.get_script_name(environ)
        path_info = environ.get('PATH_INFO', '/')
        if not path_info or path_info == script_name:
            path_info = '/'
        self.environ = environ
        self.path_info = path_info
        self.path = '%s%s' % (script_name, path_info)
        environ['PATH_INFO'] = path_info
        environ['SCRIPT_NAME'] = script_name
        self.method = environ['REQUEST_METHOD'].upper()
        self._post_parse_error = False
        if type(socket._fileobject) is type and isinstance(self.environ['wsgi.input'], socket._fileobject):
            # Under development server 'wsgi.input' is an instance of
            # socket._fileobject which hangs indefinitely on reading bytes past
            # available count. To prevent this it's wrapped in LimitedStream
            # that doesn't read past Content-Length bytes.
            #
            # This is not done for other kinds of inputs (like flup's FastCGI
            # streams) beacuse they don't suffer from this problem and we can
            # avoid using another wrapper with its own .read and .readline
            # implementation.
            #
            # The type check is done because for some reason, AppEngine
            # implements _fileobject as a function, not a class.
            try:
                content_length = int(self.environ.get('CONTENT_LENGTH', 0))
            except (ValueError, TypeError):
                content_length = 0
            self._stream = LimitedStream(self.environ['wsgi.input'], content_length)
        else:
            self._stream = self.environ['wsgi.input']
        self._read_started = False

    def __repr__(self):
        # Since this is called as part of error handling, we need to be very
        # robust against potentially malformed input.
        try:
            get = pformat(self.GET)
        except:
            get = '<could not parse>'
        if self._post_parse_error:
            post = '<could not parse>'
        else:
            try:
                post = pformat(self.POST)
            except:
                post = '<could not parse>'
        try:
            cookies = pformat(self.COOKIES)
        except:
            cookies = '<could not parse>'
        try:
            meta = pformat(self.META)
        except:
            meta = '<could not parse>'
        return '<WSGIRequest\nGET:%s,\nPOST:%s,\nCOOKIES:%s,\nMETA:%s>' % \
            (get, post, cookies, meta)

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
            self._cookies = http.parse_cookie(self.environ.get('HTTP_COOKIE', ''))
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