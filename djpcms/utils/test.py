'''Mixins for running tests with djpcms
'''
import json
import os
import sys
if sys.version_info >= (2,7):
    import unittest as test
else:
    try:
        import unittest2 as test
    except ImportError:
        print('To run tests in python 2.6 you need to install\
 the unitest2 package')
        exit(0)


# Try to import djpapps. If not available several tests won't run.
try:
    import djpapps
except:
    djpapps = None

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    BeautifulSoup = None
    
import djpcms
from djpcms import Site, WebSite, get_settings, views, forms, http
from djpcms.forms.utils import fill_form_data


skipUnless = test.skipUnless


class TestWebSite(WebSite):
    
    def __init__(self, test):
        self.test = test
        super(TestWebSite,self).__init__()
        
    def load(self):
        settings = get_settings(settings = self.settings,
                                APPLICATION_URLS = self.test.urls)
        return Site(settings)


class TestCase(test.TestCase):
        
    def website(self):
        return TestWebSite(self)
    
    def wsgi_middleware(self):
        return []
    
    def response_middleware(self):
        return []
    
    def wsgi_handler(self):
        '''Crete the WSGI handler for testing. This function invoke the
 :meth:`build_site` method which needs to be implemented by your test case.'''
        site = self.website()
        m = self.wsgi_middleware()
        site.load()
        m.append(http.WSGI(site))
        return http.WSGIhandler(m,self.response_middleware())
    
    def __resolve_test(self, path):
        '''Utility function for testing url resolver'''
        self.sites.load()
        res  = self.sites.resolve(path)  
        self.assertTrue(len(res),3)
        self.assertTrue(isinstance(res[1],views.djpcmsview))
        return res

    def bs(self, doc):
        return BeautifulSoup(doc)
    
    def urls(self, site):
        '''This should be configured by tests requiring the web
site interface. By default it return a simple view.'''
        return views.Application('/',
                    routes = (
                        views.View('/', renderer = lambda request: 'Hello!'),)
                ),
        
        
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