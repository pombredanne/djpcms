import djpcms
from djpcms import test, sites
from djpcms.apps.included.admin import AdminSite


@test.skipUnless(sites.tests.CMS_ORM,"Testing without ORM")
class TestAdmin(test.TestCase):
    
    def setUp(self):
        self.makesite()
        self.makesite('/admin/',appurls = self.sites.make_admin_urls)
    
    def testAdminSimple(self):
        '''Tests that the global sites collects admins'''
        self.sites.load()
        admins = self.sites.admins
        self.assertTrue(admins)
        
    def testAdminUrls(self):
        '''Add admins urls to sites and check the sitemap'''
        # Load sites
        self.sites.load()
        admin = self.sites.get('/admin/')
        self.assertEqual(admin.route,'/admin/')
        self.assertTrue(len(admin)) # number of admin applications positive
        node = self.node('/admin/') # get the sitemap node at the admin route
        self.assertEqual(node.path,'/admin/')
        self.assertTrue(node.view)
        self.assertTrue(node.ancestor) # The admin has an ancestor (the root node)
        children = dict(((c.path,c) for c in node.children()))
        self.assertTrue(len(children)>=2)
        a = children['/admin/layout/']
        b = children['/admin/adminapp/']
        
    def testResolver1(self):
        self.resolve_test('admin/')
        self.resolve_test('admin/layout/')
        self.resolve_test('admin/layout/templates/')
    
    