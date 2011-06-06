'''\
Test Blocks in pages
'''
from djpcms import test, sites
from djpcms.apps.included import vanilla
from djpcms.core.exceptions import PathException, Http404



@test.skipUnless(sites.tests.CMS_ORM,"Testing without ORM")
class TestPage(test.TestCase,test.PageMixin):
    
    def setUp(self):
        self.makesite()
        self.sites.load()
        self.inners = self.makeInnerTemplates()
        
    def make_page(self, url = '/'):
        self.get(url, status = 404)
        self.assertEqual(self.makepage(url).url,url)
        tree = self.sites.tree
        self.assertTrue(url in tree)
        response = self.get(url)
        page = response.context['pagelink'].page
        self.assertEqual(page.url,url)
        return page
    
    def testSimple(self):
        p = self.make_page()
        blocks = list(p.blocks())
        self.assertEqual(len(blocks),2)
        