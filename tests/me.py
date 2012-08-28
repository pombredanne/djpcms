'''Test the test suite and the package information'''
import djpcms
from djpcms.cms import ImproperlyConfigured
from djpcms.utils import test


class TestInitFile(test.TestCase):

    def test_version(self):
        self.assertTrue(djpcms.VERSION)
        self.assertTrue(djpcms.__version__)
        self.assertTrue(djpcms.__version__, djpcms.version)
        self.assertTrue(len(djpcms.VERSION) >= 2)
        
    def testLibrary(self):
        self.assertEqual(djpcms.LIBRARY_NAME, 'djpcms')
        self.assertTrue(djpcms.PACKAGE_DIR)

    def test_meta(self):
        for m in ("__author__", "__contact__", "__homepage__", "__doc__"):
            self.assertTrue(getattr(djpcms, m, None))
    
    def test_client(self):
        client = self.client()
        self.assertTrue(client)
        
    def test_client_post_json(self):
        client = self.client()
        result = client.post('/', body='bla', content_type='application/json')
        
    def test_renderer(self):
        r = djpcms.Renderer()
        self.assertEqual(r.content_type(), 'text/plain')


class TestNoFile(test.TestCase):
    
    def testNoSite(self):
        website = self.website()
        self.assertEqual(website.test, self)
        self.assertRaises(ImproperlyConfigured, website)
        
    def urls(self, site):
        return ()