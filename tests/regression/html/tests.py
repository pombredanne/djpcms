from djpcms import test, forms, html, to_string


class testHtmlTools(test.TestCase):
    
    def testAttrMixin(self):
        c = html.HtmlAttrMixin()
        c.addClass('ciao').addClass('pippo')
        self.assertTrue('ciao' in c.classes)
        self.assertTrue('pippo' in c.classes)
        f = c.flatatt()
        self.assertTrue(f in (' class="ciao pippo"',
                              ' class="pippo ciao"'))
        c = html.HtmlAttrMixin().addClass('ciao pippo bla')
        self.assertTrue(c.hasClass('bla'))
    
    def testData(self):
        c = html.HtmlAttrMixin()
        c.addData('food','pasta').addData('city','Rome')
        self.assertEqual(c.data['food'],'pasta')
        self.assertEqual(c.data['city'],'Rome')
        f = c.flatatt()
        self.assertTrue(f in (' data-food="pasta" data-city="Rome"',
                              ' data-city="Rome" data-food="pasta"'))
        
    def testNestedData(self):
        random = ['bla',3,'foo']
        table = {'name':'path',
                 'resizable':True}
        c = html.HtmlAttrMixin().addData('table',table).addData('random',random)
        self.assertEqual(c.data['table']['name'],'path')
        self.assertEqual(c.data['random'][0],'bla')
        attr = c.flatatt()
        self.assertTrue('data-table' in attr)
        
    def testEmptyAttr(self):
        c = html.HtmlAttrMixin()
        c.addAttr('value','')
        self.assertEqual(c.flatatt(),'')
        c.addAttr('value',None)
        self.assertEqual(c.flatatt(),'')
        c.addAttr('value',0)
        self.assertEqual(c.flatatt(),' value="0"')


class TestInputs(test.TestCase):
    
    def create(self, InputClass, ty, **kwargs):
        ts = InputClass(value='test', name='pippo', **kwargs)
        ht = ts.render()
        self.assertTrue(ht.startswith('<input '))
        self.assertTrue(ht.endswith('/>'))
        self.assertTrue('type="{0}"'.format(ty) in ht)
        self.assertTrue('value="test"' in ht)
        self.assertTrue('name="pippo"' in ht)
        return ts
    
    def testTextInput(self):
        self.create(html.TextInput, 'text')
        
    def testSubmitInput(self):
        self.create(html.SubmitInput, 'submit')
        
    def testPasswordInput(self):
        self.create(html.PasswordInput, 'password')
        
    def testClasses(self):
        ts = self.create(html.TextInput, 'text', cn = 'ciao')
        self.assertTrue(ts.hasClass('ciao'))
        ts = self.create(html.TextInput, 'text', cn = 'ciao ciao')
        self.assertTrue(ts.hasClass('ciao'))
        ht = ts.render()
        self.assertTrue('class="ciao"' in ht)
        ts.removeClass('ciao')
        self.assertFalse(ts.hasClass('ciao'))
        #lets try a jQuery type thing
        ts.addClass('pippo bravo').addClass('another').removeClass('bravo')
        self.assertTrue(ts.hasClass('pippo'))
        self.assertTrue(ts.hasClass('another'))
        self.assertFalse(ts.hasClass('bravo'))
        ht = ts.render()
        self.assertTrue('class="pippo another"' in ht or
                        'class="another pippo"' in ht)
        
    def testFailTextInput(self):
        self.assertRaises(TypeError,html.TextInput, fake='test')
        
    def testList(self):
        li = html.List()
        self.assertEqual(len(li),0)
        li = html.List(['a list item','another one'])
        self.assertEqual(len(li),2)
        ht = li.render()
        self.assertTrue('<ul>' in ht)
        self.assertTrue('</ul>' in ht)
        self.assertTrue('<li>a list item</li>' in ht)
        self.assertTrue('<li>another one</li>' in ht)
