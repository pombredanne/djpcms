import urllib
import sys
import os
import re
import mimetypes
import warnings

from py2py3 import ispy3k
if ispy3k():
    from io import StringIO
    from urllib.parse import urlparse, urlunparse, urlsplit, unquote,\
                             urlencode
    from http.cookies import SimpleCookie
else:
    from Cookie import SimpleCookie
    from cStringIO import StringIO
    from urlparse import urlparse, urlunparse, urlsplit, unquote
    from urllib import urlencode
    
from djpcms import sites


__all__ = ('Client', 'RequestFactory',
           'encode_file', 'encode_multipart')


BOUNDARY = 'BoUnDaRyStRiNg'
MULTIPART_CONTENT = 'multipart/form-data; boundary=%s' % BOUNDARY
CONTENT_TYPE_RE = re.compile('.*; charset=([\w\d-]+);?')


class FakePayload(object):
    """
    A wrapper around StringIO that restricts what can be read since data from
    the network can't be seeked and cannot be read outside of its content
    length. This makes sure that views can't do anything under the test client
    that wouldn't work in Real Life.
    """
    def __init__(self, content):
        self.__content = StringIO(content)
        self.__len = len(content)

    def read(self, num_bytes=None):
        if num_bytes is None:
            num_bytes = self.__len or 1
        assert self.__len >= num_bytes, "Cannot read more than the available bytes from the HTTP incoming data."
        content = self.__content.read(num_bytes)
        self.__len -= num_bytes
        return content


def store_rendered_templates(store, signal, sender, template, context, **kwargs):
    """
    Stores templates and contexts that are rendered.
    """
    store.setdefault('templates', []).append(template)
    store.setdefault('context', ContextList()).append(context)


def encode_multipart(boundary, data):
    """
    Encodes multipart POST data from a dictionary of form values.

    The key will be used as the form data name; the value will be transmitted
    as content. If the value is a file, the contents of the file will be sent
    as an application/octet-stream; otherwise, str(value) will be sent.
    """
    lines = []
    to_str = lambda s: smart_str(s, settings.DEFAULT_CHARSET)

    # Not by any means perfect, but good enough for our purposes.
    is_file = lambda thing: hasattr(thing, "read") and callable(thing.read)

    # Each bit of the multipart form data could be either a form value or a
    # file, or a *list* of form values and/or files. Remember that HTTP field
    # names can be duplicated!
    for (key, value) in data.items():
        if is_file(value):
            lines.extend(encode_file(boundary, key, value))
        elif not isinstance(value, basestring) and is_iterable(value):
            for item in value:
                if is_file(item):
                    lines.extend(encode_file(boundary, key, item))
                else:
                    lines.extend([
                        '--' + boundary,
                        'Content-Disposition: form-data; name="%s"' % to_str(key),
                        '',
                        to_str(item)
                    ])
        else:
            lines.extend([
                '--' + boundary,
                'Content-Disposition: form-data; name="%s"' % to_str(key),
                '',
                to_str(value)
            ])

    lines.extend([
        '--' + boundary + '--',
        '',
    ])
    return '\r\n'.join(lines)


def encode_file(boundary, key, file):
    to_str = lambda s: smart_str(s, settings.DEFAULT_CHARSET)
    content_type = mimetypes.guess_type(file.name)[0]
    if content_type is None:
        content_type = 'application/octet-stream'
    return [
        '--' + boundary,
        'Content-Disposition: form-data; name="%s"; filename="%s"' \
            % (to_str(key), to_str(os.path.basename(file.name))),
        'Content-Type: %s' % content_type,
        '',
        file.read()
    ]


class RequestFactory(object):
    """
    Class that lets you create mock Request objects for use in testing.

    Usage:

    rf = RequestFactory()
    get_request = rf.get('/hello/')
    post_request = rf.post('/submit/', {'foo': 'bar'})

    Once you have a request object you can pass it to any view function,
    just as if that view had been hooked up using a URLconf.
    """
    def __init__(self, **defaults):
        self.defaults = defaults
        self.cookies = SimpleCookie()
        self.errors = StringIO()

    def _base_environ(self, **request):
        """
        The base environment for a request.
        """
        environ = {
            'HTTP_COOKIE':       self.cookies.output(header='', sep='; '),
            'PATH_INFO':         '/',
            'QUERY_STRING':      '',
            'REMOTE_ADDR':       '127.0.0.1',
            'REQUEST_METHOD':    'GET',
            'SCRIPT_NAME':       '',
            'SERVER_NAME':       'testserver',
            'SERVER_PORT':       '80',
            'SERVER_PROTOCOL':   'HTTP/1.1',
            'wsgi.version':      (1,0),
            'wsgi.url_scheme':   'http',
            'wsgi.errors':       self.errors,
            'wsgi.multiprocess': True,
            'wsgi.multithread':  False,
            'wsgi.run_once':     False,
        }
        environ.update(self.defaults)
        environ.update(request)
        return environ

    def request(self, **request):
        "Construct a generic request object."
        return WSGIRequest(self._base_environ(**request))

    def get(self, path, data={}, **extra):
        "Construct a GET request"

        parsed = urlparse(path)
        r = {
            'CONTENT_TYPE':    'text/html; charset=utf-8',
            'PATH_INFO':       unquote(parsed[2]),
            'QUERY_STRING':    urlencode(data, doseq=True) or parsed[4],
            'REQUEST_METHOD': 'GET',
            'wsgi.input':      FakePayload('')
        }
        r.update(extra)
        return self.request(**r)

    def post(self, path, data={}, content_type=MULTIPART_CONTENT,
             **extra):
        "Construct a POST request."

        if content_type is MULTIPART_CONTENT:
            post_data = encode_multipart(BOUNDARY, data)
        else:
            # Encode the content so that the byte representation is correct.
            match = CONTENT_TYPE_RE.match(content_type)
            if match:
                charset = match.group(1)
            else:
                charset = settings.DEFAULT_CHARSET
            post_data = smart_str(data, encoding=charset)

        parsed = urlparse(path)
        r = {
            'CONTENT_LENGTH': len(post_data),
            'CONTENT_TYPE':   content_type,
            'PATH_INFO':      unquote(parsed[2]),
            'QUERY_STRING':   parsed[4],
            'REQUEST_METHOD': 'POST',
            'wsgi.input':     FakePayload(post_data),
        }
        r.update(extra)
        return self.request(**r)

    def head(self, path, data={}, **extra):
        "Construct a HEAD request."

        parsed = urlparse(path)
        r = {
            'CONTENT_TYPE':    'text/html; charset=utf-8',
            'PATH_INFO':       unquote(parsed[2]),
            'QUERY_STRING':    urlencode(data, doseq=True) or parsed[4],
            'REQUEST_METHOD': 'HEAD',
            'wsgi.input':      FakePayload('')
        }
        r.update(extra)
        return self.request(**r)

    def options(self, path, data={}, **extra):
        "Constrict an OPTIONS request"

        parsed = urlparse(path)
        r = {
            'PATH_INFO':       unquote(parsed[2]),
            'QUERY_STRING':    urlencode(data, doseq=True) or parsed[4],
            'REQUEST_METHOD': 'OPTIONS',
            'wsgi.input':      FakePayload('')
        }
        r.update(extra)
        return self.request(**r)

    def put(self, path, data={}, content_type=MULTIPART_CONTENT, **extra):
        "Construct a PUT request."
        if content_type is MULTIPART_CONTENT:
            post_data = encode_multipart(BOUNDARY, data)
        else:
            post_data = data

        # Make `data` into a querystring only if it's not already a string. If
        # it is a string, we'll assume that the caller has already encoded it.
        query_string = None
        if not isinstance(data, basestring):
            query_string = urlencode(data, doseq=True)

        parsed = urlparse(path)
        r = {
            'CONTENT_LENGTH': len(post_data),
            'CONTENT_TYPE':   content_type,
            'PATH_INFO':      unquote(parsed[2]),
            'QUERY_STRING':   query_string or parsed[4],
            'REQUEST_METHOD': 'PUT',
            'wsgi.input':     FakePayload(post_data),
        }
        r.update(extra)
        return self.request(**r)

    def delete(self, path, data={}, **extra):
        "Construct a DELETE request."
        parsed = urlparse(path)
        r = {
            'PATH_INFO':       unquote(parsed[2]),
            'QUERY_STRING':    urlencode(data, doseq=True) or parsed[4],
            'REQUEST_METHOD': 'DELETE',
            'wsgi.input':      FakePayload('')
        }
        r.update(extra)
        return self.request(**r)


class Client(RequestFactory):
    """
    A class that can act as a client for testing purposes.

    It allows the user to compose GET and POST requests, and
    obtain the response that the server gave to those requests.
    The server Response objects are annotated with the details
    of the contexts and templates that were rendered during the
    process of serving the request.

    Client objects are stateful - they will retain cookie (and
    thus session) details for the lifetime of the Client instance.

    This is not intended as a replacement for Twill/Selenium or
    the like - it is here to allow testing against the
    contexts and templates produced by a view, rather than the
    HTML rendered to the end-user.
    """
    def __init__(self, **defaults):
        super(Client, self).__init__(**defaults)
        self.exc_info = None

    def store_exc_info(self, **kwargs):
        """
        Stores exceptions when they are generated by a view.
        """
        self.exc_info = sys.exc_info()

    def request(self, **request):
        """The master request method. Composes the environment dictionary
and passes to the handler, returning the result of the handler."""
        environ = self._base_environ(**request)
        try:
            try:
                response = sites.wsgi(environ)
            except TemplateDoesNotExist as e:
                # If the view raises an exception, Django will attempt to show
                # the 500.html template. If that template is not available,
                # we should ignore the error in favor of re-raising the
                # underlying exception that caused the 500 error. Any other
                # template found to be missing during view error handling
                # should be reported as-is.
                if e.args != ('500.html',):
                    raise

            # Look for a signalled exception, clear the current context
            # exception data, then re-raise the signalled exception.
            # Also make sure that the signalled exception is cleared from
            # the local cache!
            if self.exc_info:
                exc_info = self.exc_info
                self.exc_info = None
                raise (exc_info[1], None, exc_info[2])

            # Save the client and request that stimulated the response.
            response.client = self
            response.request = request

            # Add any rendered template detail to the response.
            response.templates = data.get("templates", [])
            response.context = data.get("context")

            # Flatten a single context. Not really necessary anymore thanks to
            # the __getattr__ flattening in ContextList, but has some edge-case
            # backwards-compatibility implications.
            if response.context and len(response.context) == 1:
                response.context = response.context[0]

            # Provide a backwards-compatible (but pending deprecation) response.template
            def _get_template(self):
                warnings.warn("response.template is deprecated; use response.templates instead (which is always a list)",
                              PendingDeprecationWarning, stacklevel=2)
                if not self.templates:
                    return None
                elif len(self.templates) == 1:
                    return self.templates[0]
                return self.templates
            response.__class__.template = property(_get_template)

            # Update persistent cookie data.
            if response.cookies:
                self.cookies.update(response.cookies)

            return response
        finally:
            signals.template_rendered.disconnect(dispatch_uid="template-render")
            got_request_exception.disconnect(dispatch_uid="request-exception")

    def get(self, path, data={}, follow=False, **extra):
        """
        Requests a response from the server using GET.
        """
        response = super(Client, self).get(path, data=data, **extra)
        if follow:
            response = self._handle_redirects(response, **extra)
        return response

    def post(self, path, data={}, content_type=MULTIPART_CONTENT,
             follow=False, **extra):
        """
        Requests a response from the server using POST.
        """
        response = super(Client, self).post(path, data=data, content_type=content_type, **extra)
        if follow:
            response = self._handle_redirects(response, **extra)
        return response

    def head(self, path, data={}, follow=False, **extra):
        """
        Request a response from the server using HEAD.
        """
        response = super(Client, self).head(path, data=data, **extra)
        if follow:
            response = self._handle_redirects(response, **extra)
        return response

    def options(self, path, data={}, follow=False, **extra):
        """
        Request a response from the server using OPTIONS.
        """
        response = super(Client, self).options(path, data=data, **extra)
        if follow:
            response = self._handle_redirects(response, **extra)
        return response

    def put(self, path, data={}, content_type=MULTIPART_CONTENT,
            follow=False, **extra):
        """
        Send a resource to the server using PUT.
        """
        response = super(Client, self).put(path, data=data, content_type=content_type, **extra)
        if follow:
            response = self._handle_redirects(response, **extra)
        return response

    def delete(self, path, data={}, follow=False, **extra):
        """
        Send a DELETE request to the server.
        """
        response = super(Client, self).delete(path, data=data, **extra)
        if follow:
            response = self._handle_redirects(response, **extra)
        return response

    def login(self, **credentials):
        """
        Sets the Factory to appear as if it has successfully logged into a site.

        Returns True if login is possible; False if the provided credentials
        are incorrect, or the user is inactive, or if the sessions framework is
        not available.
        """
        user = authenticate(**credentials)
        if user and user.is_active \
                and 'django.contrib.sessions' in settings.INSTALLED_APPS:
            engine = import_module(settings.SESSION_ENGINE)

            # Create a fake request to store login details.
            request = HttpRequest()
            if self.session:
                request.session = self.session
            else:
                request.session = engine.SessionStore()
            login(request, user)

            # Save the session values.
            request.session.save()

            # Set the cookie to represent the session.
            session_cookie = settings.SESSION_COOKIE_NAME
            self.cookies[session_cookie] = request.session.session_key
            cookie_data = {
                'max-age': None,
                'path': '/',
                'domain': settings.SESSION_COOKIE_DOMAIN,
                'secure': settings.SESSION_COOKIE_SECURE or None,
                'expires': None,
            }
            self.cookies[session_cookie].update(cookie_data)

            return True
        else:
            return False

    def logout(self):
        """
        Removes the authenticated user's cookies and session object.

        Causes the authenticated user to be logged out.
        """
        session = import_module(settings.SESSION_ENGINE).SessionStore()
        session_cookie = self.cookies.get(settings.SESSION_COOKIE_NAME)
        if session_cookie:
            session.delete(session_key=session_cookie.value)
        self.cookies = SimpleCookie()

    def _handle_redirects(self, response, **extra):
        "Follows any redirects by requesting responses from the server using GET."

        response.redirect_chain = []
        while response.status_code in (301, 302, 303, 307):
            url = response['Location']
            scheme, netloc, path, query, fragment = urlsplit(url)

            redirect_chain = response.redirect_chain
            redirect_chain.append((url, response.status_code))

            if scheme:
                extra['wsgi.url_scheme'] = scheme

            # The test client doesn't handle external links,
            # but since the situation is simulated in test_client,
            # we fake things here by ignoring the netloc portion of the
            # redirected URL.
            response = self.get(path, QueryDict(query), follow=False, **extra)
            response.redirect_chain = redirect_chain

            # Prevent loops
            if response.redirect_chain[-1] in response.redirect_chain[0:-1]:
                break
        return response