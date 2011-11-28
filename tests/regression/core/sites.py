import djpcms
from djpcms import views, http
from djpcms.utils import test, zip

    
class TestSites(test.TestCase):

    def testCreate(self):
        '''Simply make a site container'''
        site = djpcms.ApplicationSites()
        self.assertEqual(site.route.rule,'')
        self.assertFalse(site)
        self.assertEqual(site.settings,None)
        self.assertEqual(site.Page,None)
        self.assertEqual(site.User,None)
        self.assertEqual(site.storage,None)
        self.assertEqual(site.search_engine,None)
        self.assertEqual(site.root,site)
        self.assertEqual(site.parent,None)
        self.assertFalse(site.isloaded)
        
    def testCreate2(self):
        '''Simply make a site container'''
        site = djpcms.ApplicationSites('/bla/')
        self.assertEqual(site.route.rule,'bla/')
        self.assertEqual(site.route,site.rel_route)
        
    def testSetParent(self):
        site = djpcms.ApplicationSites()
        def set_parent():
            site.parent = site
        self.assertRaises(ValueError, set_parent)
        self.assertEqual(site.parent,None)
        site.parent = None
        self.assertEqual(site.route,site.rel_route)
        
    def testMake(self):
        loader = djpcms.SiteLoader()
        settings = loader.get_settings(__file__)
        sites = djpcms.ApplicationSites()
        s = sites.make(settings)
        self.assertEqual(len(sites),1)
        self.assertEqual(s.route.rule,'')
        

