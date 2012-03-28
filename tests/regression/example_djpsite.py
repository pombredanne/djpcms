from djpcms.utils import test

from djpsite.manage import WebSite


class TestInitFile(test.TestCase):
    
    def website(self):
        return WebSite()
    
    def testSite(self):
        site = self.website()()
        self.assertTrue(site)
        
    def test404(self):
        client = self.client()
        r = client.get('/jcsdcdscdscdscsdc/', status_code = 404)
        
        
        
        