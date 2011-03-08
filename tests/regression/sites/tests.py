from py2py3 import zip

from djpcms import test
from djpcms.apps.site import ApplicationSites
from djpcms.utils import SLASH
from djpcms.core.exceptions import ImproperlyConfigured


class TestSites(test.TestCase):
    '''Tests the sites singletone'''    
    def makesite(self):
        self.sites = ApplicationSites()
        
    def testLoadError(self):
        '''No sites created. Load should raise an ImproperlyConfigured
        error'''
        self.assertRaises(ImproperlyConfigured,self.sites.load)

    def testMultipleSitesOrdering(self):
        sites = self.sites
        MakeSite = sites.make
        tsites = ['']*3
        tsites[2] = MakeSite(__file__)
        tsites[0] = MakeSite(__file__, route = '/admin/secret/')
        tsites[1] = MakeSite(__file__, route = '/admin/')
        self.assertEqual(len(self.sites),3)
        for s,t in zip(self.sites,tsites):
            self.assertEqual(s,t)
            
    def testTreeSimple(self):
        '''Simple Tree testing'''
        sites = self.sites
        MakeSite = sites.make
        tsites = ['']*3
        tsites[2] = MakeSite(__file__)
        tsites[0] = MakeSite(__file__, route = '/admin/secret/')
        tsites[1] = MakeSite(__file__, route = '/admin/')
        self.assertEqual(sites.tree,None)
        sites.load()
        root = sites.tree.root
        self.assertEqual(root.url,SLASH)
        self.assertEqual(len(root.children),1)
        self.assertTrue('/admin/' in root.children)
        node = root.children['/admin/']
        self.assertTrue('/admin/secret/' in node.children)
        node = node.children['/admin/secret/']
        self.assertEqual(len(node.children),0)
        self.assertEqual(len(sites.tree),3)
        
    def testUser(self):
        sites = self.sites
        self.assertEqual(sites.User,None)
