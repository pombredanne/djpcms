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
        sites = self.sites
        admins = sites.admins
        self.assertTrue(admins)

    def testAdminSimple2(self):
        sites = self.sites
        admin = sites.make_admin_urls(name = 'Great Admin')[0]
        self.assertTrue(isinstance(admin,AdminSite))
        self.assertEqual(admin.description,'Great Admin')
        self.assertEqual(admin.name,'great_admin')
        self.assertEqual(len(admin.views),1)
        self.assertEqual(admin.baseurl,'/')
        self.assertEqual(admin.application_site,None)
        
    def testAdminUrls(self):
        '''Add admins urls to sites and check the sitemap'''
        # admin is an instance of ApplicationsSite
        ap = self.admin_route
        admin = self.makeadmin()
        admin.load()
        self.assertEqual(admin.route,ap)
        self.assertEqual(len(admin),1)
        node = djpcms.node(ap)
        self.assertEqual(node.path,ap)
        children = dict(((c.path,c) for c in node.children()))
        self.assertTrue(len(children)>=2)
        a = children[ap+'djpcms/']
        b = children[ap+'adminapp/']
        
    
    