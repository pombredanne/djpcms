import datetime

from djpcms import test, views, sites


@test.skipUnless(sites.tests.CMS_ORM,"Testing without ORM")
class TestApplicationNavigation(test.TestCase, test.PageMixin):
    appurls = 'regression.navigation.appurls.appurls'
    
    def setUp(self):
        from .models import Strategy
        self.Strategy = Strategy
        self.makesite()
        self.sites.load()
        
    def testSimpleApplication(self):
        self.assertEqual(self.makepage('/', site = self.sites).url,'/')
        p = self.makepage('random', in_navigation = -1)
        self.assertEqual(p.url,'/random/')
        self.assertEqual(p.in_navigation,-1)
        context = self.get().context
        sitenav = context["sitenav"].items()
        self.assertEqual(len(sitenav),4)
        self.assertEqual(sitenav[0].url,'/random/')
        snav = sitenav[0].items()
        self.assertEqual(len(snav),0)
        #
        # now lets login
        # self.assertTrue(self.login())
        # context = self.get()
        # snav = list(list(context["sitenav"])[1])
        # self.assertEqual(len(snav),1)
        # self.assertEqual(snav[0].url,'/strategies/add/')
        
    def _testApplicationWithMultiPage(self):
        '''We create some specialised pages for some Strategy objects and
check that they appear in navigation.'''
        Strategy = self.Strategy
        Strategy(name='the good').save()
        Strategy(name='the bad').save()
        Strategy(name='the ugly').save()
        ps = self.makepage('search', Strategy)
        p0 = self.makepage('view', Strategy)
        p1 = self.makepage('view', Strategy, bit='1', in_navigation = 2)
        p2 = self.makepage('view', Strategy, bit='2', in_navigation = 1)
        self.assertNotEqual(p1,p0)
        self.assertNotEqual(p2,p1)
        context = self.get()
        sitenav = list(context["sitenav"])
        self.assertEqual(len(sitenav),1)     
        self.assertEqual(sitenav[0].url,'/strategies/')
        snav = list(sitenav[0])
        self.assertEqual(len(snav),2)
        #
        context = self.get('/strategies/')
        sitenav = list(context["sitenav"])
        self.assertEqual(len(sitenav),1)  
        self.assertEqual(sitenav[0].url,'/strategies/')
        snav = list(sitenav[0])
        self.assertEqual(len(snav),2)
        #
        context = self.get('/strategies/3/')
        self.assertEqual(context['page'],p0)
        context = self.get('/strategies/1/')
        self.assertEqual(context['page'],p1)
        context = self.get('/strategies/2/')
        self.assertEqual(context['page'],p2)
        
