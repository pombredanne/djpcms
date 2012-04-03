from stdnet import orm

from . import base

class TestDjpSite(base.TestCase):
        
    def testSite(self):
        site = self.site
        self.assertTrue(site)
        self.assertTrue(site.Page)
        
    def testUser(self):
        # User should have an application in admin and main site
        site = self.site
        self.assertTrue(site.User)

    def testPageLayout(self):
        site = self.website()()
        page = site.get_page_layout('default')
        self.assertTrue(page)
        keys = list(page.children)
        self.assertEqual(len(keys),4)
        content = page.children['content']
        self.assertEqual(content.numblocks,0)
        
    def test404(self):
        client = self.client()
        r = client.get('/jcsdcdscdscdscsdc/', status_code = 404)
        
    def testAdmin(self):
        user = self.create_user(login = True)
        client = self.client()
        response = client.get('/admin/')
        self.assertTrue(user)
        
        