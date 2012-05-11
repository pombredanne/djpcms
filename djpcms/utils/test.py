'''Mixins for running tests with djpcms'''
import json
import os
import re
import sys
if sys.version_info >= (2,7):   # pragma nocover
    import unittest as test
else:   # pragma nocover
    try:
        import unittest2 as test
    except ImportError:
        print('To run tests in python 2.6 you need to install\
 the unittest2 package')
        exit(0)

try:
    from BeautifulSoup import BeautifulSoup
except ImportError: # pragma nocover
    BeautifulSoup = None
    
import djpcms
from djpcms import Site, WebSite, get_settings, views, forms, http
from djpcms.forms.utils import fill_form_data

from py2py3 import BytesIO

from .http import native_str, to_bytes, SimpleCookie, urlencode, unquote,\
                  urlparse

skipUnless = test.skipUnless
main = test.main

CONTENT_TYPE_RE = re.compile('.*; charset=([\w\d-]+);?')


class TestWebSite(WebSite):
    can_pickle = False
    def __init__(self, test):
        self.test = test
        super(TestWebSite,self).__init__()
        
    def load(self):
        return self.test.load_site(self)
    
    def finish(self):
        '''Once the site has loaded, we create new tables.'''
        self.site.clear_model_tables()
        self.site.create_model_tables()
        self.test.add_initial_db_data()


class TestCase(test.TestCase):
    '''A :class:`TestCase` class which adds the :meth:`website` method for 
easy testing web site applications. To use the Http client you need
to derive from this class.'''
    installed_apps = ('djpcms',)
    settings = None
    web_site_callbacks = []
        
    def website(self):
        '''Return a :class:`djpcms.WebSite` loader, a callable object
returning a :class:`djpcms.Site`. Tipical usage::
        
    website = self.website()
    
    site = website()
    wsgi = website.wsgi()
'''
        website = TestWebSite(self)
        website.callbacks.extend(self.web_site_callbacks)
        return website
        
    def load_site(self, website):
        settings = get_settings(settings = self.settings,
                                APPLICATION_URLS = self.urls,
                                INSTALLED_APPS = self.installed_apps)
        website.add_wsgi_middleware(self.wsgi_middleware())
        website.add_response_middleware(self.response_middleware())
        return Site(settings)
    
    def client(self, **defaults):
        website = self.website()
        settings = website().settings
        wsgi = website.wsgi()
        return HttpTestClientRequest(self, wsgi, settings, **defaults)
    
    def wsgi_middleware(self):
        '''Override this method to add wsgi middleware to the test site
WSGI handler.'''
        return []
    
    def response_middleware(self):
        '''Override this method to add response middleware to the test site
WSGI handler.'''
        return []

    def bs(self, doc):  # pragma nocover
        return BeautifulSoup(doc)
    
    def urls(self, site):
        '''This should be configured by tests requiring the web
site interface. By default it return a simple view.'''
        return views.Application('/',
                    routes = (
                        views.View('/', renderer = lambda request: 'Hello!'),)
                ),
                
    def add_initial_db_data(self):
        pass

        
class TestCaseWidthAdmin(TestCase):
    
    def load_site(self, website):
        from djpcms.apps.admin import make_admin_urls
        site = super(TestCaseWidthAdmin,self).load_site(website)
        settings_admin = djpcms.get_settings(self.settings,
                                APPLICATION_URLS  = make_admin_urls(),
                                INSTALLED_APPS = self.installed_apps)
        site.addsite(settings_admin, route = '/admin/')
        return site
    
    
class PluginTest(TestCase):
    plugin = None
    
    def _pre_setup(self):
        super(PluginTest,self)._pre_setup()
        module = self.plugin.__module__
        self.site.settings.DJPCMS_PLUGINS = [module]
        
    def _simplePage(self):
        c = self.get('/')
        p = c['page']
        p.set_template(p.create_template('simple','{{ content0 }}','content'))
        b = p.add_plugin(self.plugin)
        self.assertEqual(b.plugin_name,self.plugin.name)
        self.assertEqual(b.plugin,self.plugin())
        return c
        
    def request(self, user = None):
        req = http.Request()
        req.user = user
        return req
        
    def testBlockOutOfBound(self):
        p = self.get('/')['page']
        self.assertRaises(BlockOutOfBound, p.add_plugin, self.plugin)
        
    def testSimple(self):
        self._simplePage()
    
    def testEdit(self):
        from djpcms.plugins import SimpleWrap
        '''Test the editing view by getting a the view and the editing form
and sending AJAX requests.'''
        c = self._simplePage()
        # we need to login to perform editing
        self.assertTrue(self.login())
        # get the editing page for '/'
        ec = self.get(self.editurl('/'))
        # '/' and editing page '/' are the same
        self.assertEqual(c['page'],ec['page'])
        # inner editing page
        inner = ec['inner']
        # beautiful soup the block content
        bs = self.bs(inner).find('div', {'id': 'blockcontent-1-0-0'})
        self.assertTrue(bs)
        f  = bs.find('form')
        self.assertTrue(f)
        action = dict(f.attrs)['action']
        # get the prefix
        prefix = bs.find('input', attrs = {'name':'_prefixed'})
        self.assertTrue(prefix)
        prefix = dict(prefix.attrs)['value']
        self.assertTrue(prefix)
        
        # Send bad post request (no data)
        res = self.post(action, {}, ajax = True, response = True)
        self.assertEqual(res['content-type'],'application/javascript')
        body = json.loads(res.content)
        self.assertFalse(body['error'])
        self.assertEqual(body['header'],'htmls')
        
        for msg in body['body']:
            if msg['identifier'] != '.form-messages':
                self.assertEqual(msg['html'][:26],'<ul class="errorlist"><li>')
        
        data = {'plugin_name': self.plugin.name,
                'container_type': SimpleWrap.name}
        data.update(self.get_plugindata(f))
        pdata = dict(((prefix+'-'+k,v) for k,v in data.items()))
        pdata['_prefixed'] = prefix
        res = self.post(action, pdata, ajax = True, response = True)
        self.assertEqual(res['content-type'],'application/javascript')
        body = json.loads(res.content)
        self.assertFalse(body['error'])
        
        preview = False
        for msg in body['body']:
            if msg['identifier'] == '#plugin-1-0-0-preview':
                html = msg['html']
                preview = True
                break
        self.assertTrue(preview)
        
    def testRender(self):
        self.testEdit()
        c = self.get('/')
        inner = c['inner']
        bs = self.bs(inner).find('div', {'class': 'djpcms-block-element plugin-{0}'.format(self.plugin.name)})
        self.assertTrue(bs)
        return bs
    
    def get_plugindata(self, soup_form, request = None):
        '''To be implemented by derived classes'''
        form = self.plugin.form
        return fill_form_data(form(request = request)) if form else {}
    

BOUNDARY = 'BoUnDaRyStRiNg'
MULTIPART_CONTENT = 'multipart/form-data; boundary=%s' % BOUNDARY

def encode_multipart(boundary, data):
    """
    Encodes multipart POST data from a dictionary of form values.

    The key will be used as the form data name; the value will be transmitted
    as content. If the value is a file, the contents of the file will be sent
    as an application/octet-stream; otherwise, str(value) will be sent.
    """
    lines = []
    # Not by any means perfect, but good enough for our purposes.
    is_file = lambda thing: hasattr(thing, "read") and\
                             hasattr(thing.read,'__call__')

    # Each bit of the multipart form data could be either a form value or a
    # file, or a *list* of form values and/or files. Remember that HTTP field
    # names can be duplicated!
    for (key, value) in data.items():
        value = native_str(value)
        if is_file(value):
            lines.extend(encode_file(boundary, key, value))
        elif not isinstance(value,str) and hasattr(value,'__iter__'):
            for item in value:
                if is_file(item):
                    lines.extend(encode_file(boundary, key, item))
                else:
                    lines.extend([
                        '--' + boundary,
                        'Content-Disposition: form-data; name="%s"' % to_str(key),
                        '',
                        item
                    ])
        else:
            lines.extend([
                '--' + boundary,
                'Content-Disposition: form-data; name="{0}"'.format(key),
                '',
                str(value)
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


class Response(object):
    
    def __init__(self, environ):
        self.environ = environ
        self.status = None
        self.response_headers = None
        self.exc_info = None
        self.response = None
        
    def __call__(self, status, response_headers, exc_info=None):
        '''Mock the wsgi start_response callable'''
        self.status = status
        self.response_headers = response_headers
        self.exc_info = exc_info
        
    @property
    def status_code(self):
        if self.status:
            return int(self.status.split()[0])
        
        
class HttpTestClientRequest(object):
    """Class that lets you create mock HTTP environment objects for use
in testing."""
    def __init__(self, test, handler, settings, **defaults):
        self.test = test
        self.settings = settings
        self.handler = handler
        self.defaults = defaults
        self.cookies = SimpleCookie()
        self.errors = BytesIO()
        self.response_data = None

    def _base_environ(self, ajax = False, **request):
        """The base environment for a request.
        """
        cookie = self.cookies
        if isinstance(cookie, SimpleCookie):
            cookie = self.cookies.output(header='', sep='; ')
        environ = {
            'HTTP_COOKIE': cookie,
            'PATH_INFO': '/',
            'QUERY_STRING': '',
            'REMOTE_ADDR': '127.0.0.1',
            'REQUEST_METHOD': 'GET',
            'SCRIPT_NAME': '',
            'SERVER_NAME': 'testserver',
            'SERVER_PORT': '80',
            'SERVER_PROTOCOL': 'HTTP/1.1',
            'wsgi.version': (1,1),
            'wsgi.url_scheme': 'http',
            'wsgi.errors': self.errors,
            'wsgi.multiprocess': False,
            'wsgi.multithread': False,
            'wsgi.run_once': False,
        }
        environ.update(self.defaults)
        environ.update(request)
        if ajax:
            environ['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        return environ

    def request(self, status_code, **request):
        "Build a fake HTTP request."
        environ = self._base_environ(**request)
        r = Response(environ)
        r.response = self.handler(environ, r)
        if r.response_headers is not None:
            # The request has finished
            for head, value in r.response_headers:
                if head.lower() == 'set-cookie':
                    self.cookies = value
            self.test.assertEqual(r.response.status_code, status_code)
        return r
        
    def get(self, path, data={}, ajax = False, status_code = 200, **extra):
        "Construct a GET request"
        parsed = urlparse(path)
        r = {
            'CONTENT_TYPE':    'text/html; charset=utf-8',
            'PATH_INFO':       unquote(parsed[2]),
            'QUERY_STRING':    urlencode(data, doseq=True) or parsed[4],
            'REQUEST_METHOD': 'GET',
            'wsgi.input':      BytesIO()
        }
        r.update(extra)
        return self.request(status_code, **r)
    
    def post(self, path, data={}, content_type=MULTIPART_CONTENT,
             status_code = 200, **extra):
        "Construct a POST request."
        if content_type is MULTIPART_CONTENT:
            post_data = encode_multipart(BOUNDARY, data)
        else:
            match = CONTENT_TYPE_RE.match(content_type)
            charset = match.group(1) if match else self.settings.DEFAULT_CHARSET
            post_data = to_bytes(data, encoding=charset)

        parsed = urlparse(path)
        r = {
            'CONTENT_LENGTH': len(post_data),
            'CONTENT_TYPE':   content_type,
            'PATH_INFO':      unquote(parsed[2]),
            'QUERY_STRING':   parsed[4],
            'REQUEST_METHOD': 'POST',
            'wsgi.input':     BytesIO(post_data),
        }
        r.update(extra)
        return self.request(status_code, **r)
    
    def head(self, path, data={}, **extra):
        "Construct a HEAD request."

        parsed = urlparse(path)
        r = {
            'CONTENT_TYPE':    'text/html; charset=utf-8',
            'PATH_INFO':       unquote(parsed[2]),
            'QUERY_STRING':    urlencode(data, doseq=True) or parsed[4],
            'REQUEST_METHOD': 'HEAD',
            'wsgi.input':      BytesIO()
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
            'wsgi.input':      BytesIO()
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
            'wsgi.input':     BytesIO(post_data),
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
            'wsgi.input':      BytesIO()
        }
        r.update(extra)
        return self.request(**r)
    

################################################################################
##    PLUGINS FOR TESTING WITH NOSE OR PULSAR
################################################################################
try:
    import nose
except ImportError:
    nose = None
    
try:
    import pulsar
except ImportError:
    pulsar = None
    
try:
    from stdnet import test as stdnet_test
except ImportError:
    stdnet_test = None

def addoption(argv, *vals, **kwargs):
    '''Add additional options to the *argv* list.'''
    if vals:
        for val in vals:
            if val in argv:
                return
        argv.append(vals[0])
        value = kwargs.get('value')
        if value is not None:
            argv.append(value)


def start(argv=None, modules=None, nose_options=None, description=None,
          version=None, plugins=None):
    '''Start djpcms tests. Use this function to start tests for
djpcms aor djpcms applications. It check for pulsar and nose
and add testing plugins.'''
    global pulsar
    argv = argv or sys.argv
    description = description or 'Djpcms Asynchronous test suite'
    version = version or djpcms.__version__
    if len(argv) > 1 and argv[1] == 'nose':
        pulsar = None
        sys.argv.pop(1)
    if pulsar:
        os.environ['djpcms_test_suite'] = 'pulsar'
        from pulsar.apps.test import TestSuite
        from pulsar.apps.test.plugins import profile
        from djpcms.core.management.commands.run_pulsar import AsyncTestPlugin
        if stdnet_test and plugins is None:
            plugins = [stdnet_test.PulsarStdnetServer()]
        plugins = plugins or []
        plugins.extend((AsyncTestPlugin(),
                        profile.Profile()))
        suite = TestSuite(modules=modules,
                          plugins=plugins,
                          description=description,
                          version=version)
        suite.start()
    elif nose:
        os.environ['djpcms_test_suite'] = 'nose'
        if stdnet_test and plugins is None:
            plugins = [stdnet_test.NoseStdnetServer()]
        argv = list(argv)
        if nose_options:
            nose_options(argv)
        nose.main(argv=argv, addplugins=plugins)
    else:
        raise NotImplementedError(
                    'To run tests you need either pulsar or nose.')
        