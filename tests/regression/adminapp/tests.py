import djpcms
from djpcms import test, sites
from djpcms.apps.included.admin import AdminSite



def admin_urls():
    return sites.make_admin_urls(name=  'admin')


@test.skipUnless(sites.tests.CMS_ORM,"Testing without ORM")
class TestAdmin(test.TestCase):
    admin_route = '/admin/'
    
    def makeadmin(self, route = None, appurls = None):
        return self.makesite(route = route or self.admin_route,
                             appurls = admin_urls)
        
    
    def testAdminSimple(self):
        '''Tests that the global sites collects admins'''
        self.sites.load()
        admins = self.sites.admins
        self.assertTrue(admins)
        
    def testAdminUrls(self):
        '''Add admins urls to sites and check the sitemap'''
        # admin is an instance of ApplicationsSite
        ap = self.admin_route
        admin = self.makeadmin()
        # Load sites
        self.sites.load()
        self.assertEqual(admin.route,ap)
        self.assertTrue(len(admin)) # number of admin applications positive
        node = djpcms.node(ap) # get the sitemap node at the admin route
        self.assertEqual(node.path,ap)
        self.assertTrue(node.view)
        self.assertTrue(node.ancestor) # The admin has an ancestor (the root node)
        children = dict(((c.path,c) for c in node.children()))
        self.assertTrue(len(children)>=2)
        a = children[ap+'djpcms/']
        b = children[ap+'adminapp/']
        
    
    