import djpcms
from djpcms import views, http, Route, ImproperlyConfigured, AlreadyRegistered
from djpcms.utils import test, zip


def get_simpleapps():
    return (
        views.Application('/bla/',
            name = 'app2',
            routes = (views.View(renderer = lambda djp : 'ciao bla'),
                      views.View('pluto/',\
                                    renderer = lambda djp : 'ciao bla view2'))
        ),
        views.Application('/',
            name = 'app1',
            routes = (views.View(renderer = lambda djp : 'ciao'),)
        ),
    )

    
class TestApplication(test.TestCase):

    def setUp(self):
        settings = djpcms.get_settings(__file__,
                                       APPLICATION_URLS = get_simpleapps)
        self.site = site = djpcms.Site(settings = settings)
        self.assertEqual(site.parent,None)
        self.assertEqual(site.path,'/')
        
    def testContruction(self):
        site = self.site
        self.assertEqual(len(site),0)
        app = views.Application('/',
                    name = 'luca',
                    routes = (views.View(renderer = lambda djp : 'ciao'),))
        self.assertFalse(app.isbound)
        self.assertEqual(app.parent,None)
        self.assertEqual(app.count(),1)
        self.assertEqual(len(app),1)
        self.assertFalse(site.isbound)
        
    def testSimpleBindning(self):
        # set the application urls manually
        site = self.site
        self.assertFalse(site.isbound)
        urls = site.urls()
        self.assertEqual(len(urls),2)
        self.assertTrue(site.isbound)
        for app in urls:
            self.assertTrue(app.isbound)
            self.assertEqual(app.parent,site)
            self.assertEqual(app.root,site)
            
    def testSimpleResolve(self):
        site = self.site
        handle, kwargs = site.resolve('')

    def __testImproperlyConfigured(self):
        '''No sites created. Load should raise an ImproperlyConfigured
        error'''
        self.assertRaises(ImproperlyConfigured,self.sites.load)
        
    def __testNoUser(self):
        sites = self.sites
        self.assertEqual(sites.User,None)
        

class TestTree(object):
    '''Tests the sites singletone'''
    
    def setUp(self):
        self.sites = djpcms.Site()
        settings = djpcms.get_settings(__file__,
                                       APPLICATION_URLS = get_simpleapps)
        self.sites.make(settings)
        
    def testSimple(self):
        '''Simple Tree testing'''
        sites = self.sites
        self.assertFalse(sites.is_loaded)
        self.assertEqual(len(sites),1)
        tsites[0] = self.make(sites.settings, route = '/admin/secret/')
        tsites[1] = self.make(sites.settings, route = '/admin/')
        tsites[2] = self.make(sites.settings)
        
    def __testTreeSimple(self):
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
