from djpcms import html
from djpcms.utils import test


class testAttributes(test.TestCase):
    
    def testClass(self):
        c = html.Widget()
        c.addClass('ciao').addClass('pippo')
        self.assertTrue('ciao' in c.classes)
        self.assertTrue('pippo' in c.classes)
        f = c.flatatt()
        self.assertTrue(f in (" class='ciao pippo'",
                              " class='pippo ciao'"))
        c = html.Widget().addClass('ciao pippo bla')
        self.assertTrue(c.hasClass('bla'))
        
    def testMakerClass(self):
        template = html.WidgetMaker(cn = 'bla foo')
        c = template().addClass('ciao').addClass('pippo')
        self.assertEqual(c.classes,set(('bla','foo','ciao','pippo')))
    
    def testData(self):
        c = html.Widget()
        c.addData('food','pasta').addData('city','Rome')
        self.assertEqual(c.data['food'],'pasta')
        self.assertEqual(c.data['city'],'Rome')
        f = c.flatatt()
        self.assertTrue(f in (" data-food='pasta' data-city='Rome'",
                              " data-city='Rome' data-food='pasta'"))
        
    def testNestedData(self):
        random = ['bla',3,'foo']
        table = {'name':'path',
                 'resizable':True}
        c = html.Widget().addData('table',table).addData('random',random)
        self.assertEqual(c.data['table']['name'],'path')
        self.assertEqual(c.data['random'][0],'bla')
        attr = c.flatatt()
        self.assertTrue('data-table' in attr)
        
    def testEmptyAttr(self):
        c = html.Widget()
        c.addAttr('value','')
        self.assertEqual(c.flatatt(),'')
        c.addAttr('value',None)
        self.assertEqual(c.flatatt(),'')
        c.addAttr('value',0)
        self.assertEqual(c.flatatt()," value='0'")


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
        
        
class TestInputs(test.TestCase):
    
    def create(self, name, ty, **kwargs):
        ts = html.Widget(name, value='test', name='pippo', **kwargs)
        ht = ts.render()
        self.assertTrue(ht.startswith('<input '))
        self.assertTrue(ht.endswith('/>'))
        self.assertTrue("type='{0}'".format(ty) in ht)
        self.assertTrue("value='test'" in ht)
        self.assertTrue("name='pippo'" in ht)
        return ts
    
    def testTextInput(self):
        self.create('input:text', 'text')
    
    def testDisabled(self):
        ts = self.create('input:text', 'text', disabled = 'disabled')
        ht = ts.render()
        self.assertTrue("disabled='disabled'" in ht)
            
    def testReadonly(self):
        ts = self.create('input:text', 'text', readonly = 'readonly')
        ht = ts.render()
        self.assertTrue("readonly='readonly'" in ht)
        
    def testSubmitInput(self):
        self.create('input:submit', 'submit')
        
    def testPasswordInput(self):
        self.create('input:password', 'password')
        
    def testClasses(self):
        ts = self.create('input:text', 'text', cn = 'ciao')
        self.assertTrue(ts.hasClass('ciao'))
        ts = self.create('input:text', 'text', cn = 'ciao ciao')
        self.assertTrue(ts.hasClass('ciao'))
        ht = ts.render()
        self.assertTrue("class='ciao'" in ht)
        ts.removeClass('ciao')
        self.assertFalse(ts.hasClass('ciao'))
        #lets try a jQuery type thing
        ts.addClass('pippo bravo').addClass('another').removeClass('bravo')
        self.assertTrue(ts.hasClass('pippo'))
        self.assertTrue(ts.hasClass('another'))
        self.assertFalse(ts.hasClass('bravo'))
        ht = ts.render()
        self.assertTrue("class='pippo another'" in ht or
                        "class='another pippo'" in ht)
        
        

