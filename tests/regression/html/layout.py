from djpcms.utils import test
from djpcms import html
from djpcms.html.layout import *


class TestLayout(test.TestCase):
    
    def testBasePage(self):
        # this is just an empty page layout
        page_template = page()
        self.assertEqual(page_template.tag,'div')
        self.assertEqual(page_template.data,{'role':'page'})
        self.assertEqual(page_template.numblocks, 0)
        self.assertFalse(page_template.is_block())
        self.assertRaises(ValueError, page_template.add, self)
        #
        pg = page_template()
        text = pg.render()
        self.assertEqual(text,"<div data-role='page'><div></div></div>")
        html = pg.render(context = {'content': 'Hello World!'})
        self.assertEqual(html,
                "<div data-role='page'><div>Hello World!</div></div>")
        
    def testPage(self):
        page_template = page(
                container('topbar',
                          grid('grid 100'), cn='topbar-fixed'),
                container('header',
                          grid('grid 100'), role = 'header'),
                container('content', role = 'content'),
                container('footer',
                          grid('grid 33-33-33'), role = 'footer'))
        self.assertEqual(page_template.numblocks, 5)
        self.assertEqual(len(page_template.children), 4)
        pg = page_template()
        text = pg.render(context = {'content': 'Hello World!'})
        self.assertTrue('Hello World!' in text)
        keys = list(page_template.keys())
        self.assertEqual(len(keys), 4)
        
    def testSimpleColumn(self):
        col = column(1,4)
        self.assertEqual(col.numblocks, 1)
        d = col.block_dictionary()
        self.assertEqual(d,{0:col})
        self.assertTrue(col.is_block())
        self.assertRaises(ValueError, column, 2)
        
    def testNestingColumns(self):
        '''Create a column containing a container.'''
        col = column(1,2, Grid(grid('grid 100'), grid('grid 50-50')))
        self.assertEqual(col.numblocks,3)
        self.assertFalse(col.is_block())
        
    def testGetGrid(self):
        self.assertRaises(LayoutDoesNotExist, grid, 'sjdcbhsjcbjshcbjscb')
        all_grids = grids()
        self.assertTrue('grid 50-50' in all_grids)
        self.assertTrue('grid 33-33-33' in all_grids)
        self.assertTrue('grid 25-25-25-25' in all_grids)
        
        