'''Blocks in pages'''
import os

import djpcms
from djpcms.utils import test


@test.skipUnless(os.environ['stdcms'],"Requires stdcms installed")
class TestPage(test.TestCase):
        
    def make_page(self, url = '/'):
        client = self.client()
        client.get(url, status = 404)
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
        