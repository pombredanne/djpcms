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
        html = pg.render()
        self.assertEqual(html,"<div data-role='page'></div>")
        pg = page_template('Hello World!')
        html = pg.render()
        self.assertEqual(html,"<div data-role='page'>Hello World!</div>")
        
    def testPage(self):
        page_template = page(
                container('topbar',
                          get_grid('grid 100'), cn='topbar-fixed'),
                container('header',
                          get_grid('grid 100'), role = 'header'),
                container('content', role = 'content'),
                container('footer',
                          get_grid('grid 33-33-33'), role = 'footer'))
        self.assertEqual(page_template.numblocks, 5)
        self.assertEqual(len(page_template.children), 4)
        pg = page_template()
        text = pg.render(context = {'content': 'Hello World!'})
        self.assertTrue('Hello World!' in text)
        
    def testSimpleColumn(self):
        col = column(1,4)
        self.assertEqual(col.numblocks, 1)
        d = col.block_dictionary()
        self.assertEqual(d,{0:col})
        self.assertTrue(col.is_block())
        self.assertRaises(ValueError, column, 2)
        
    def testNestingColumns(self):
        '''Create a column containing a container.'''
        col = column(1,2, grid(row(column(1,1)),
                               row(column(1,2), column(1,2))))
        self.assertEqual(col.numblocks,3)
        self.assertFalse(col.is_block())
        
    def testGetLayout(self):
        self.assertRaises(LayoutDoesNotExist, get_layout, 'sjdcbhsjcbjshcbjscb')
        default = get_layout('default')
        self.assertTrue(isinstance(default,page))
        self.assertEqual(default.numblocks,0)
        self.assertEqual(page_layouts(), ['default'])
        self.assertTrue('content' in default.children)
        inner = get_layout('Grid 100', grid=True)
        
        