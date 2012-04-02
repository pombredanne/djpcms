from djpcms.utils import test

from djpsite.manage import WebSite


class TestDjpSite(test.TestCase):
    
    def website(self):
        return WebSite()
    
    def testSite(self):
        site = self.website()()
        self.assertTrue(site)

    def testPageLayout(self):
        site = self.website()()
        page = site.get_page_layout('default')
        self.assertTrue(page)
        keys = list(page.keys())
        self.assertEqual(len(keys),4)
        content = page.children['content']
        self.assertEqual(content.numblocks,0)
        
    def test404(self):
        client = self.client()
        r = client.get('/jcsdcdscdscdscsdc/', status_code = 404)
        