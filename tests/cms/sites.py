from djpcms import views, cms
from djpcms.utils.httpurl import zip
from djpcms.utils import test

    
class TestSites(test.TestCase):

    def testCreate(self):
        '''Simply make a site container'''
        site = cms.Site()
        self.assertEqual(site.route.rule,'')
        self.assertFalse(site)
        self.assertTrue(site.settings)
        self.assertEqual(site.Page,None)
        self.assertEqual(site.User,None)
        self.assertEqual(site.storage,None)
        self.assertEqual(site.search_engine,None)
        self.assertEqual(site.root,site)
        self.assertEqual(site.parent,None)
        self.assertFalse(site.isbound)
        self.assertRaises(cms.ImproperlyConfigured, site.urls)
        self.assertFalse(site.isbound)
        
    def testCreate2(self):
        '''Simply make a site container'''
        site = cms.Site(route='/bla/')
        self.assertEqual(site.route.rule,'bla/')
        self.assertEqual(site.route,site.rel_route)
        
    def testSimple(self):
        '''Simple Tree testing'''
        site = cms.Site()
        self.assertFalse(site.isbound)
        self.assertEqual(site.path,'/')
        self.assertEqual(len(site),0)
        si = [site.addsite(route = '/admin/secret/'),
              site.addsite(route = '/admin/'),
              site.addsite()]
        self.assertEqual(len(site),3)
        sites = list(site)
        self.assertEqual(len(sites),3)
        self.assertEqual(sites,si)
        self.assertFalse(site.isbound)
        self.assertRaises(cms.ImproperlyConfigured, site.urls)
        self.assertFalse(site.isbound)
        
    def testAddLeaf(self):
        site = cms.Site()
        site1 = site.addsite(route='bla')
        self.assertFalse(site1.route.is_leaf)
        route = cms.Route('foo')
        self.assertTrue(route.is_leaf)
        site = self.assertRaises(ValueError,
                                 lambda : site.addsite(route=route))
        
    def testMakeWithRoute(self):
        site = cms.Site(route = 'bla')
        site1 = site.addsite()
        self.assertNotEqual(site1.route,site1.rel_route)
        self.assertEqual(site1.path,'/bla/')
        self.assertEqual(site1.rel_route.path,'/')
        self.assertEqual(len(site),1)
        self.assertFalse(site.isbound)
        self.assertRaises(cms.ImproperlyConfigured, site.load)
        self.assertFalse(site.isbound)
        