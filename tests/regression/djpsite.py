from djpcms.utils import test

from examples.djpsite.manage import WebSite


class TestInitFile(test.TestCase):
    
    def website(self):
        return WebSite()
    
    def testSite(self):
        site = self.website()()
        self.assertTrue(site)
        
        