from djpcms import html
from djpcms.utils import test


class TestWidgets(test.TestCase):
    
    def testAncor(self):
        a = html.Widget('a', 'kaput', cn = 'bla', href = '/abc/')
        self.assertEqual(a.attrs['href'],'/abc/')
        ht = a.render()
        self.assertTrue('>kaput</a>' in ht)
        a = html.Widget('a', xxxx = 'ciao')
        self.assertFalse('xxxx' in a.attrs)
        self.assertEqual(a.internal['xxxx'],'ciao')
    
    def testList(self):
        li = html.Widget('ul')
        self.assertEqual(li.tag,'ul')
        self.assertEqual(len(li),0)
        li = html.Widget('ul', ['a list item','another one'])
        self.assertEqual(len(li),2)
        ht = li.render()
        self.assertTrue('<ul>' in ht)
        self.assertTrue('</ul>' in ht)
        self.assertTrue('<li>a list item</li>' in ht)
        self.assertTrue('<li>another one</li>' in ht)
        
    def testTabs(self):
        tab = html.tabs()
        self.assertEqual(tab.tag,'div')
        tab.add('tab1','this is tab 1')
        self.assertEqual(len(tab),1)
        tab.add('tab2','this is tab 2')
        self.assertEqual(len(tab),2)
        ht = tab.render()
        self.assertTrue('ui-tabs' in ht)


