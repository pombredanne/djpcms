'''Mixins for running tests with djpcms'''
import json
import os
import re
import sys
from collections import Mapping
from io import StringIO

from pulsar.apps.test import unittest, HttpTestClient

try:
    from BeautifulSoup import BeautifulSoup
except ImportError: # pragma nocover
    BeautifulSoup = None

import djpcms
from djpcms import views, forms
from djpcms.cms import Site, WebSite, get_settings, fetch_command, Request
from djpcms.cms.request import RequestCache
from djpcms.cms.formutils import fill_form_data
from djpcms.utils import orms
from djpcms.utils.httpurl import Headers

from .httpurl import native_str, to_bytes, SimpleCookie, urlencode, unquote,\
                     urlparse, ispy3k

if ispy3k:
    from io import StringIO as Stream
else:   #pragma    nocover
    from io import BytesIO as Stream

skipUnless = unittest.skipUnless
CONTENT_TYPE_RE = re.compile('.*; charset=([\w\d-]+);?')


class TestWebSite(WebSite):
    '''The website for testing. It delegates the loading to the
:meth:`TestCase.load_site` method.'''
    def __init__(self, test):
        self.test = test
        super(TestWebSite, self).__init__()

    def load(self):
        return self.test.load_site(self)

    def finish(self):
        '''Once the site has loaded, we create new tables.'''
        self.site.clear_model_tables()
        self.site.create_model_tables()
        self.test.add_initial_db_data()


class TestCase(unittest.TestCase):
    '''A :class:`TestCase` class which adds the :meth:`website` method for
easy testing web site applications.'''
    installed_apps = ('djpcms',)
    settings = None
    web_site_callbacks = []

    def _pre_setup(self):
        self.site()
        self.flush()

    def _post_teardown(self):
        self.flush()

    #    DJPCMS SPECIFIC UTILITY METHODS
    def flush(self):
        orms.flush_models()
        
    def website(self):
        '''Return a :class:`djpcms.cms.WebSite`.'''
        if not hasattr(self, '_website'):
            self._website = TestWebSite(self)
            self._website.callbacks.extend(self.web_site_callbacks)
        return self._website

    def site(self):
        return self.website()()

    def load_site(self, website):
        '''Called by the *website* itself. Don't call directly unless you know
what you are doing. Override if you need more granular control.'''
        settings=get_settings(settings=self.settings,
                                APPLICATION_URLS=self.urls,
                                INSTALLED_APPS=self.installed_apps)
        website.add_wsgi_middleware(self.wsgi_middleware())
        website.add_response_middleware(self.response_middleware())
        return Site(settings)

    def fetch_command(self, command, argv=None):
        '''Fetch a command.'''
        argv = ('test',) + tuple(argv or ())
        cmd = fetch_command(self.website(), command, argv,
                            stdout=Stream(), stderr=Stream())
        self.assertTrue(cmd.logger)
        self.assertEqual(cmd.name, command)
        return cmd

    def client(self, **kwargs):
        website = self.website()
        return HttpTestClient(self, website.wsgi(), **kwargs)

    def dummy_request(self, url='/', instance=None, **environ):
        request = Request(environ, None, instance, url)
        environ['DJPCMS'] = RequestCache(request)
        return request
    
    def form_data(self, data, prefix=''):
        if prefix:
            data = dict((('%s%s' % (k,prefix), v) for k,v in data.items()))
        data[forms.PREFIX_KEY] = prefix
        return data

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


################################################################################
##    PLUGINS FOR TESTING WITH NOSE OR PULSAR
################################################################################
try:
    import nose
except ImportError: #pragma    nocover
    nose = None

try:
    from stdnet import test as stdnet_test
except ImportError: #pragma    nocover
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
    use_nose = False
    argv = argv or sys.argv
    description = description or 'Djpcms Asynchronous test suite'
    version = version or djpcms.__version__
    if len(argv) > 1 and argv[1] == 'nose':
        use_nose = True
        sys.argv.pop(1)
    if use_nose:
        os.environ['djpcms_test_suite'] = 'nose'
        if stdnet_test and plugins is None:
            plugins = [stdnet_test.NoseStdnetServer()]
        argv = list(argv)
        if nose_options:
            nose_options(argv)
        nose.main(argv=argv, addplugins=plugins)
    else:
        os.environ['djpcms_test_suite'] = 'pulsar'
        from pulsar.apps.test import TestSuite
        from pulsar.apps.test.plugins import bench, profile
        if stdnet_test and plugins is None:
            plugins = (stdnet_test.PulsarStdnetServer(),
                       bench.BenchMark(),
                       profile.Profile())
        suite = TestSuite(modules=modules,
                          plugins=plugins,
                          description=description,
                          version=version)
        suite.start()
