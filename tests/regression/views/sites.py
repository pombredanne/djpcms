import djpcms
from djpcms import views, http, Route, ImproperlyConfigured, AlreadyRegistered
from djpcms.utils import test, zip


def get_simpleapps():
    return (
        views.Application(
            '/',
            name = 'app1',
            views = (
                     ('home',views.View(renderer = lambda djp : 'ciao')),
                     )
        ),
        views.Application(
            '/bla/',
            name = 'app2',
            views = (
                ('home',views.View(renderer = lambda djp : 'ciao bla')),
                ('view2',views.View('pluto/',\
                                     renderer = lambda djp : 'ciao bla view2'))
                )
        )
    )

    
class TestSites(test.TestCase):

    def testMake(self):
        '''Simply make a site'''
        sites = self.sites
        settings = self.loader.get_settings(__file__)
        site = sites.make(settings)
        self.assertEqual(site.parent,sites)
        self.assertEqual(str(site.route),'')
        self.assertEqual(site.route,site.rel_route)
        self.assertRaises(AlreadyRegistered,lambda : sites.make(settings))
        self.assertEqual(len(sites),1)
        self.assertFalse(sites.isloaded)
        sites.load()
        self.assertTrue(sites.isloaded)
        
    def testMake2(self):
        '''make 2 sites'''
        sites = self.sites
        settings = self.loader.get_settings(__file__)
        site1 = sites.make(settings)
        self.assertEqual(site1.route,site1.rel_route)
        site2 = sites.make(settings,'/extra/')
        self.assertEqual(site2.route,site2.rel_route)
        self.assertEqual(str(site2.route),'extra/')
        self.assertEqual(len(sites),2)
        self.assertFalse(sites.isloaded)
        sites.load()
        self.assertTrue(sites.isloaded)
        
    def testMakeWithRoute(self):
        sites = djpcms.ApplicationSites(route = 'bla')
        settings = self.loader.get_settings(__file__)
        site1 = sites.make(settings)
        self.assertNotEqual(site1.route,site1.rel_route)
        self.assertEqual(str(site1.route),'bla/')
        self.assertEqual(str(site1.rel_route),'')
        self.assertEqual(len(sites),1)
        self.assertFalse(sites.isloaded)
        self.assertRaises(ImproperlyConfigured, sites.load)
        self.assertTrue(sites.isloaded)
        
    def testMakeLeaf(self):
        sites = self.sites
        settings = self.loader.get_settings(__file__)
        site = sites.make(settings,'bla')
        self.assertFalse(site.route.is_leaf)
        route = Route('foo')
        self.assertTrue(route.is_leaf)
        site = self.assertRaises(ValueError,
                                 lambda : sites.make(settings,route))
    
    
class TestApplication(test.TestCase):
    
    def __testMultipleSitesOrdering(self):
        sites = self.sites
        settings = self.loader.get_settings(__file__)
        tsites = ['']*3
        tsites[2] = self.makesite()
        tsites[0] = self.makesite(route = '/admin/secret/')
        tsites[1] = self.makesite(route = '/admin/')
        self.assertEqual(len(self.sites),3)
        for s,t in zip(self.sites,tsites):
            self.assertEqual(s,t)    

    def __testImproperlyConfigured(self):
        '''No sites created. Load should raise an ImproperlyConfigured
        error'''
        self.assertRaises(ImproperlyConfigured,self.sites.load)
        
    def __testNoUser(self):
        sites = self.sites
        self.assertEqual(sites.User,None)
        

class TestTree(object):
    '''Tests the sites singletone'''

    def testTreeSimple(self):
        '''Simple Tree testing'''
        tsites = ['']*3
        tsites[2] = self.makesite()
        tsites[0] = self.makesite(route = '/admin/secret/')
        tsites[1] = self.makesite(route = '/admin/')
        self.assertEqual(self.sites.tree,None)
        self.sites.load()
        tree = self.sites.tree
        root = tree.root
        self.assertEqual(len(tree),3)
        self.assertEqual(root.path,'/')
        children = root.children_map()
        self.assertEqual(len(children),1)
        self.assertTrue('/admin/' in children)
        node = children['/admin/']
        children = node.children_map()
        self.assertTrue('/admin/secret/' in children)
        node = children['/admin/secret/']
        children = node.children_map()
        self.assertEqual(len(children),0)
        
    def testTreeWithApps(self):
        self._makeApps()
        
    def testResolverWithApps(self):
        site = self._makeApps()
        s,view,kwargs = self.resolve_test('bla/')
        self.assertEqual(kwargs,{})
        self.assertEqual(s,site)
        self.assertEqual(view.path,'/bla/')
        s,view,kwargs = self.resolve_test('bla/pluto/')
        self.assertEqual(kwargs,{})
        self.assertEqual(s,site)
        self.assertEqual(view.path,'/bla/pluto/')
        
    def testResolver404(self): 
        site = self._makeApps()
        self.assertRaises(http.Http404,
                          lambda : self.resolve_test('bla/extra/'))
    
    def _makeApps(self):
        site = self.makesite(appurls = get_simpleapps)
        self.assertEqual(len(self.sites),1)
        self.sites.load()
        self.assertEqual(len(site),2)
        tree = site.tree
        self.assertTrue('/' in tree)
        self.assertTrue('/bla/' in tree)
        node = tree['/']
        self.assertTrue(node.children)
        node = tree['/bla/']
        self.assertTrue(node.children)
        return site
