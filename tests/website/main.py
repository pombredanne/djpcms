from . import base


class TestDjpSite(base.TestCase):
        
    def testSite(self):
        site = self.site()
        self.assertTrue(site)
        self.assertTrue(site.Page)
        
    def testUser(self):
        # User should have an application in admin and main site
        site = self.site()
        self.assertTrue(site.User)

    def testPageLayout(self):
        site = self.website()()
        page = site.get_page_layout('default')
        self.assertTrue(page)
        keys = list(page.children)
        self.assertEqual(len(keys),4)
        content = page.children['content']
        self.assertEqual(content.numcolumns,0)
        
    def test404(self):
        client = self.client()
        url = '/jcsdcdscdscdscsdc/'
        r = client.get(url, status_code=404)
        self.assertEqual(r.environ['PATH_INFO'], url)
        
    def testHome(self):
        client = self.client()
        url = '/'
        r = client.get(url, status_code=200)
        self.assertEqual(r.headers['content-type'], 'text/html')
        self.assertEqual(r.environ['PATH_INFO'], url)
        
    def testAdmin(self):
        user = self.create_user(login=True)
        client = self.client()
        response = client.get('/admin/')
        self.assertTrue(user)
        
        