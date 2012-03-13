from djpcms.html import layout
from djpcms.utils import test

class TestLayout(test.TestCase):
    
    def testBase(self):
        # this is just an empty page layout
        page_template = layout.page()
        self.assertEqual(page_template.tag,'div')
        self.assertEqual(page_template.data,{'role':'page'})
        page = page_template()
        html = page.render()
        self.assertEqual(html,"<div data-role='page'></div>")
        page = page_template('Hello World!')
        html = page.render()
        self.assertEqual(html,"<div data-role='page'>Hello World!</div>")
        self.assertEqual(page_template.numblocks(),0)
        
    def testHeadBodyFooter(self):
        page_template = layout.get_layout('header-content-footer')
        self.assertEqual(page_template.tag,'div')
        self.assertEqual(len(page_template.allchildren),3)