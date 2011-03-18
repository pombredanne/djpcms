from djpcms import test, sites
from djpcms.apps.included import vanilla
from djpcms.core.exceptions import PathException


def appurls():
    from .models import Strategy
    return (vanilla.Application('/strategies/',Strategy),)


@test.skipUnless(sites.tests.CMS_ORM,"Testing without ORM")
class TestPage(test.TestCase,test.PageMixin):
    appurls = 'regression.page.tests.appurls'
    
    def setUp(self):
        # Load up a site to make sure the Page and InnerTemplate models are registered with a backend
        from .models import Strategy
        self.model = Strategy
        self.makesite()
        self.sites.load()
        self.inners = self.makeInnerTemplates()
        self.appmodel = self.sites.for_model(Strategy)
        
    def testRoot(self):
        self.assertEqual(self.makepage('/').url,'/')
        response = self.get()
        page = response.context['pagelink'].page
        self.assertEqual(page.url,'/')
        
    def testModelSearchPage(self):
        view = self.appmodel.getview('search')
        p = self.makepage(view.path())
        self.assertEqual(p.url,view.path())
        response = self.get('/strategies/')
        page = response.context['pagelink'].page
        self.assertEqual(page.url,'/strategies/')
        node = response.DJPCMS.tree['/strategies/']
        self.assertEqual(node.path,'/strategies/')
        root = node.ancestor
        # There is no parent view, since nothing is defined at root
        self.assertRaises(PathException, root.get_view)
        
    def testObjectView(self):
        '''Test an object view with a page'''
        self.model(name = 'test').save()
        view = self.appmodel.getview('view')
        self.assertEqual(view.path(),'/strategies/%(id)s/')
        self.assertEqual(self.makepage(view.path()).url,view.path())
        response = self.get('/strategies/1/')
        page = response.context['pagelink'].page
        self.assertTrue(page)
        
    def testFlatPageChildOfFlatPage(self):
        self.assertEqual(self.makepage('/').url,'/')
        self.assertEqual(self.makepage('/about/').url,'/about/')
        response = self.get('/about/')
        response = self.get('/ciao/', status = 404)
        self.assertEqual(self.makepage('/about/bla/').url,'/about/bla/')
        response = self.get('/about/bla/')
        
    def _testObjectViewSpecial(self):
        self.assertEqual(self.makepage('/').url,'/')
        self.assertEqual(self.makepage('/about/').url,'/about/')
        Strategy = self.model
        Strategy(name = 'test1').save()
        Strategy(name = 'test2').save()
        sp = self.makepage('search',Strategy)
        sp = self.makepage('search',Strategy,'blabla',fail=True)
        vp = self.makepage('view',Strategy)
        vp1 = self.makepage('view',Strategy,'1')
        self.assertNotEqual(vp,vp1)
        self.assertEqual(vp.application,vp1.application)
        self.assertEqual(vp.parent,vp1.parent)
        self.assertFalse(vp.url_pattern)
        self.assertTrue(vp1.url_pattern)
        self.assertNotEqual(vp.url,vp1.url)
        context = self.get('/strategies/2/')
        page = context['page']
        djp  = context['djp']
        self.assertEqual(page,vp)
        context = self.get('/strategies/1/')
        page1 = context['page']
        self.assertEqual(page1,vp1)
        djp1 = context['djp']
        self.assertEqual(djp.view,djp1.view)
        self.assertEqual(djp.view.code,djp1.view.code)
        
    def _testObjectViewSpecialChild(self):
        Strategy = self.model
        Strategy(name = 'test1').save()
        Strategy(name = 'test2').save()
        sp = self.makepage('search',Strategy)
        vp = self.makepage('view',Strategy)
        vp1 = self.makepage('view',Strategy,'1')
        vp1 = self.makepage('view',Strategy,'2')
        ep = self.makepage('edit',Strategy)
        #self.assertEqual(ep.parent,vp)
    
