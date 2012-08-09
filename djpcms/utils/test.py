'''Mixins for running tests with djpcms'''
import json
import os
import re
import sys
from collections import Mapping

from pulsar.apps.test import unittest, HttpTestClient

try:
    from BeautifulSoup import BeautifulSoup
except ImportError: # pragma nocover
    BeautifulSoup = None

import djpcms
from djpcms import views, forms
from djpcms.cms import Site, WebSite, get_settings
from djpcms.cms.formutils import fill_form_data
from djpcms.utils import orms
from djpcms.utils.httpurl import Headers

from .httpurl import native_str, to_bytes, SimpleCookie, urlencode, unquote,\
                     urlparse, BytesIO

skipUnless = unittest.skipUnless

CONTENT_TYPE_RE = re.compile('.*; charset=([\w\d-]+);?')


class TestWebSite(WebSite):
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


class TestCase(unittest.TestCase):
    '''A :class:`TestCase` class which adds the :meth:`website` method for
easy testing web site applications. To use the Http client you need
to derive from this class.'''
    installed_apps = ('djpcms',)
    settings = None
    web_site_callbacks = []

    def _pre_setup(self):
        orms.flush_models()

    def _post_teardown(self):
        orms.flush_models()

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

    def site(self):
        if not hasattr(self, '_site'):
            self._site = self.website()()
        return self._site

    def load_site(self, website):
        '''Called by the *website* itself. Don't call directly unless you know
what you are doing.'''
        settings=get_settings(settings=self.settings,
                                APPLICATION_URLS=self.urls,
                                INSTALLED_APPS=self.installed_apps)
        website.add_wsgi_middleware(self.wsgi_middleware())
        website.add_response_middleware(self.response_middleware())
        return Site(settings)

    def client(self, **kwargs):
        website = self.website()
        return HttpTestClient(self, website.wsgi(), **kwargs)

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
        settings_admin = get_settings(self.settings,
                                      APPLICATION_URLS=make_admin_urls(),
                                      INSTALLED_APPS=self.installed_apps)
        site.addsite(settings_admin, route='/admin/')
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
        if stdnet_test and plugins is None:
            plugins = (stdnet_test.PulsarStdnetServer(),
                       profile.Profile())
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
