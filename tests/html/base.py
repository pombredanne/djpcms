from djpcms import html, Renderer
from djpcms.utils import test

w = html.Widget

class TestBaseClasses(test.TestCase):

    def testRenderer(self):
        r = Renderer()
        self.assertRaises(NotImplementedError, r.render)
        self.assertEqual(r.media(None), None)

    def testWidgetClass(self):
        t = html.WidgetMaker(tag = 'span', key = 'test')
        self.assertEqual(t.tag, 'span')
        self.assertEqual(t.widget_class, w)
        self.assertEqual(t.key, 'test')
        self.assertTrue('test' in str(t))
        self.assertEqual(t.css(),{})
        d = {'display':'none', 'overflow':'hidden'}
        self.assertEqual(t.css(d),t)
        self.assertEqual(t.css(),d)


class TestAttributes(test.TestCase):

    def testWidegtRepr(self):
        c = w('div', cn='bla')
        self.assertEqual(c.content_type(), 'text/html')
        self.assertEqual(str(c), "<div class='bla'>")
        c = w(cn='bla')
        self.assertEqual(c.tag, None)
        self.assertEqual(str(c), 'Widget(WidgetMaker)')

    def testClass(self):
        c = w().addClass('ciao').addClass('pippo')
        self.assertTrue('ciao' in c.classes)
        self.assertTrue('pippo' in c.classes)
        f = c.flatatt()
        self.assertTrue(f in (" class='ciao pippo'",
                              " class='pippo ciao'"))
        c = w().addClass('ciao pippo bla')
        self.assertTrue(c.hasClass('bla'))

    def testMakerClass(self):
        template = html.WidgetMaker(cn = 'bla foo')
        c = template().addClass('ciao').addClass('pippo')
        self.assertEqual(c.classes,set(('bla','foo','ciao','pippo')))

    def testData(self):
        c = w()
        c.addData('food','pasta').addData('city','Rome')
        self.assertEqual(c.data['food'],'pasta')
        self.assertEqual(c.data['city'],'Rome')
        f = c.flatatt()
        self.assertTrue(f in (" data-food='pasta' data-city='Rome'",
                              " data-city='Rome' data-food='pasta'"))
        c.addData('food','risotto')
        self.assertEqual(c.data['food'],'risotto')

    def testNestedData(self):
        random = ['bla',3,'foo']
        table = {'name':'path',
                 'resizable':True}
        c = w().addData('table',table).addData('random',random)
        self.assertEqual(c.data['table']['name'],'path')
        self.assertEqual(c.data['table']['resizable'],True)
        self.assertEqual(c.data['random'][0],'bla')
        attr = c.flatatt()
        self.assertTrue('data-table' in attr)
        c.addData('table',{'resizable':False,'rows':40})
        self.assertEqual(c.data['table']['name'],'path')
        self.assertEqual(c.data['table']['resizable'],False)
        self.assertEqual(c.data['table']['rows'],40)

    def testEmptyAttr(self):
        c = w('input:text')
        c.addAttr('value', None)
        self.assertEqual(c.attr('value'), None)
        self.assertEqual(c.flatatt(), " type='text'")
        c.addAttr('value', '')
        self.assertEqual(c.attr('value'),'')
        self.assertTrue(" value=''" in c.flatatt())
        c.addAttr('value', 0)
        self.assertTrue(" value='0'" in c.flatatt())
        self.assertEqual(c.attr('value'), 0)

    def testEmptyAttribute(self):
        opt = w('option', '--------', value='')
        self.assertEqual(opt.attr('value'), '')
        text = opt.render()
        self.assertTrue(" value=''" in text)
        
    def testHide(self):
        c = w('div', 'foo').hide()
        self.assertEqual(c.flatatt(), " style='display:none;'")
        c.show()
        self.assertEqual(c.flatatt(), "")


class TestInputs(test.TestCase):

    def create(self, name, ty, **kwargs):
        ts = w(name, value='test', name='pippo', **kwargs)
        ht = ts.render()
        self.assertTrue(ht.startswith('<input '))
        self.assertTrue(ht.endswith('/>'))
        self.assertTrue("type='{0}'".format(ty) in ht)
        self.assertTrue("value='test'" in ht)
        self.assertTrue("name='pippo'" in ht)
        return w(name, value='test', name='pippo', **kwargs)

    def testTextInput(self):
        self.create('input:text', 'text')

    def testDisabled(self):
        ts = self.create('input:text', 'text', disabled = 'disabled')
        ht = ts.render()
        self.assertTrue("disabled='disabled'" in ht)

    def testReadonly(self):
        ts = self.create('input:text', 'text', readonly='readonly')
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
        ts._streamed = False
        ht = ts.render()
        self.assertTrue("class='pippo another'" in ht or
                        "class='another pippo'" in ht)



