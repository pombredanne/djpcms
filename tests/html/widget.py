from djpcms import html
from djpcms.utils import test

w = html.Widget


class TestInputs(test.TestCase):
    
    def testSubmit(self):
        s = html.SubmitInput()
        self.assertTrue(s.hasClass('button'))
        self.assertEqual(s.attr('type'),'submit')

class TestWidgets(test.TestCase):
    
    def testAncor(self):
        a = w('a', 'kaput', cn = 'bla', href = '/abc/')
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
        self.assertEqual(len(tab),0)
        self.assertEqual(tab.tag, 'div')
        tab.addtab('tab1','this is tab 1')
        self.assertEqual(len(tab),2)
        tab.addtab('tab2','this is tab 2')
        self.assertEqual(len(tab),3)
        ht = tab.render()
        self.assertTrue('ui-tabs' in ht)
        
    def testAccordion(self):
        acc = html.accordion()
        self.assertEqual(len(acc),0)
        self.assertEqual(acc.tag, 'div')
        acc.addtab('tab1','this is tab 1')
        self.assertEqual(len(acc),2)
        acc.addtab('tab2','this is tab 2')
        self.assertEqual(len(acc),4)
        ht = acc.render()
        self.assertTrue('ui-accordion-container' in ht)

    def testBox(self):
        box = html.box(hd='This is a box', bd='bla bla ...')
        self.assertEqual(len(box), 2)
        text = box.render()
        box = html.box(hd='This is a box', bd='bla bla ...', ft='...')
        self.assertEqual(len(box), 3)

    def testBoxMenu(self):
        box = html.box(hd='This is a box', bd='bla bla ...', collapsable=True)
        self.assertEqual(len(box), 2)

    def testDefinitionList(self):
        dl = w('dl', [('first','bla'),('second','foo'),('third','pippo')])
        self.assertEqual(len(dl), 6)
        text = dl.render()
        self.assertTrue('dt' in text)
        self.assertTrue('dd' in text)