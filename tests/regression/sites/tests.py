from py2py3 import zip

from djpcms import sites, test, MakeSite
from djpcms.apps.site import ApplicationSites
from djpcms.core.exceptions import ImproperlyConfigured


class TestSites(test.TestCase):
    
    def makesite(self):
        self.sites = ApplicationSites()
        
    def MakeSite(self,*args,**kwargs):
        return self.sites.make(*args,**kwargs)
        
    def testLoadError(self):
        '''No sites created. Load should raise an ImproperlyConfigured
        error'''
        self.assertRaises(ImproperlyConfigured,self.sites.load)

    def testMultipleSitesOrdering(self):
        MakeSite = self.MakeSite
        tsites = ['']*3
        tsites[2] = MakeSite(__file__)
        tsites[0] = MakeSite(__file__, route = '/admin/secret/')
        tsites[1] = MakeSite(__file__, route = '/admin/')
        self.assertEqual(len(self.sites),3)
        for s,t in zip(self.sites,tsites):
            self.assertEqual(s,t)
        
    def testUser(self):
        sites = self.sites
        self.assertEqual(sites.User,None)
