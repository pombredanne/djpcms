'''Test the test suite and the package information'''
import djpcms as package
from djpcms import ImproperlyConfigured
from djpcms.utils import test


class TestInitFile(test.TestCase):

    def test_version(self):
        self.assertTrue(package.VERSION)
        self.assertTrue(package.__version__)
        v = tuple((int(v) for v in package.__version__.split('.')))
        self.assertEqual(v,package.VERSION)
        self.assertTrue(len(package.VERSION) >= 2)
        
    def testLibrary(self):
        self.assertEqual(package.LIBRARY_NAME,'djpcms')
        self.assertTrue(package.PACKAGE_DIR)

    def test_meta(self):
        for m in ("__author__", "__contact__", "__homepage__", "__doc__"):
            self.assertTrue(getattr(package, m, None))
    
    def test_client(self):
        client = self.client()
        self.assertTrue(client)
        middleware = client.handler.middleware
        self.assertTrue(middleware)
        self.assertTrue(middleware[-1].site)


class TestNoFile(test.TestCase):
    
    def testNoSite(self):
        website = self.website()
        self.assertEqual(website.test, self)
        self.assertRaises(ImproperlyConfigured, website)
        
    def urls(self, site):
        return ()