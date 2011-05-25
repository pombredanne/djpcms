import json
import os
import sys
import unittest
from copy import copy

import djpcms
from djpcms.apps.site import ApplicationSites
from djpcms import forms, UnicodeMixin, http
from djpcms.views import djpcmsview
from djpcms.forms.utils import fill_form_data
from djpcms.utils.importer import import_module
from djpcms.core.exceptions import *

from .client import Client
from .mixin import UserMixin

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    skip = unittest.skip
    skipIf = unittest.skipIf
    skipUnless = unittest.skipUnless
    SkipTest = unittest.SkipTest
    TestCaseBase = unittest.TestCase
    TextTestRunner = unittest.TextTestRunner
    TestSuiteBase = unittest.TestSuite
except AttributeError:
    from .skiptests import *


__all__ = ['TestCase','ApplicationTest',
           'PluginTest','skip', 'skipIf',
           'skipUnless', 'SkipTest',
           'TestDirectory', 'ContribTestDirectory',
           'SiteTestDirectory']


class TestDirectory(UnicodeMixin):
    
    def __init__(self,path):
        self.path = path
        
    def __unicode__(self):
        return self.path
    
    def app_label(self,test_type,app):
        return '{0}.{1}'.format(test_type,app)
    
    def dirpath(self, test_name):
        return os.path.join(self.path,test_name)
        
    def test_module(self, test_name, mod):
        return '{0}.tests'.format(mod)


class ContribTestDirectory(TestDirectory):

    def __init__(self, lib, contrib):
        self.lib = lib
        self.contrib = contrib
        module = import_module('{0}.{1}'.format(lib,contrib))
        self.path = os.path.dirname(module.__file__)
        
    def dirpath(self, test_name):
        return self.path

    def app_label(self, test_type, app):
        return '{0}.{1}.{2}'.format(self.lib,self.contrib,app)
        
    def test_module(self, test_name, mod):
        return '{0}.tests.{1}'.format(mod,test_name)

def SiteTestDirectory(TestDirectory):
    pass


class ApplicationTest(TestCaseBase):
    '''Test Class for djpcms applications'''
    _env = None
    
    def _pre_setup(self):
        self.sites = djpcms.sites
        self.handler = http.DjpCmsHandler(self.sites)
        if self._env:
            self._env.pre_setup()
    
    def node(self, path):
        return self.sites.tree[path]

    def __call__(self, result=None):
        """Wrapper around default __call__ method to perform common test
        set up.
        """
        skipping = getattr(self.__class__, "__unittest_skip__", False)
        if not skipping:
            self._pre_setup()
        self.client = Client(self.handler)
        super(ApplicationTest, self).__call__(result)
        if not skipping:
            self._post_teardown()
            
    def _post_teardown(self):
        if self._env:
            self._env.post_teardown()

    def post(self, url = '/', data = {}, status = 200,
             response = False, ajax = False):
        '''Quick function for posting some content'''
        if ajax:
            resp = self.client.post(url,data,HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        else:
            resp = self.client.post(url,data)
        self.assertEqual(resp.status_code,status)
        if response:
            return resp
        else:
            return resp.context
    
    def get(self, url = '/', status = 200, response = False,
            ajax = False):
        '''Quick function for getting some content'''
        if ajax:
            resp = self.client.get(url,HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        else:
            resp = self.client.get(url)
        self.assertEqual(resp.status_code,status)
        return resp


class TestCase(ApplicationTest):
    '''Test class for testing djpcms itself.
Implements shortcut functions for testing djpcms.
Must be used as a base class for TestCase classes'''
    def _pre_setup(self):
        from djpcms.models import tree_update
        self.sites = ApplicationSites() # The test sites handler. Used for everything
        if tree_update:
            tree_update.register_site(self.sites)
        self.handler = http.DjpCmsHandler(self.sites)
        self.tests = djpcms.sites.settings
        self.tests.TESTING = True
        if self._env:
            self._env.pre_setup()
            
    def _post_teardown(self):
        from djpcms.models import tree_update
        if tree_update:
            tree_update.unregister_site(self.sites)
            
    def makesite(self, route = None, appurls = None, **kwargs):
        '''Utility function for setting up an application site. The site is not loaded.'''
        appurls = getattr(self,'appurls',appurls)
        tests = self.tests
        apps = tests.INSTALLED_APPS + self.installed_apps()
        for app in tests.INCLUDE_TEST_APPS:
            if app not in apps:
                apps.append(app)
        return self.sites.make(self.tests.SITE_DIRECTORY,
                               'conf',
                               route = route or '/',
                               CMS_ORM = tests.CMS_ORM,
                               TEMPLATE_ENGINE = tests.TEMPLATE_ENGINE,
                               APPLICATION_URLS = appurls,
                               INSTALLED_APPS = apps,
                               MIDDLEWARE_CLASSES = tests.MIDDLEWARE_CLASSES)
        
    def installed_apps(self):
        return []
        
    def resolve_test(self, path):
        '''Utility function for testing url resolver'''
        self.sites.load()
        res  = self.sites.resolve(path)  
        self.assertTrue(len(res),3)
        self.assertTrue(isinstance(res[1],djpcmsview))
        return res

    def bs(self, doc):
        return BeautifulSoup(doc)
        
        
class PluginTest(TestCase,UserMixin):
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
    