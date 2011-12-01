'''Blocks in pages'''
import djpcms
from djpcms.utils import test


@test.skipUnless(test.djpapps,"Requires djpapps installed")
class TestPage(test.TestCase):
    
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
    
    def __testSimple(self):
        p = self.make_page()
        blocks = list(p.blocks())
        self.assertEqual(len(blocks),2)
        