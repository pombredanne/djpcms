from djpcms.utils import test


class TestFormLayout(test.TestCase):
    
    def testNotField(self):
        from djpcms import forms
        from djpcms.forms import layout as uni
        from djpcms.apps.contentedit import PageForm
        htmlform = forms.HtmlForm(PageForm,
                                  layout=uni.FormLayout(
                                            uni.Fieldset('random')))
        layout = htmlform['layout']
        fs = layout[1]
        self.assertTrue('random' in fs.children)
        w = fs()
        #self.assertEqual(w.inputs, [])
        text = w.render(context = {'random': 'Hello'})
        self.assertTrue('Hello' in text)
        
    def testLegend(self):
        from djpcms import forms
        from djpcms.forms import layout as uni
        from djpcms.apps.contentedit import PageForm
        htmlform = forms.HtmlForm(PageForm,
                            layout = uni.FormLayout(
                                uni.Fieldset(legend = 'This is a legend')))
        layout = htmlform['layout']
        fs = layout[1]
        self.assertEqual(fs.legend_html, 'This is a legend')
        text = htmlform().render()
        self.assertTrue('This is a legend</div>' in text)
        
    def testColumns(self):
        from djpcms import forms
        from djpcms.forms import layout as uni
        from djpcms.html.layout import grid
        c = uni.Columns('field1','field2')
        self.assertEqual(c.grid, grid('grid 50-50'))
        # test error
        self.assertRaises(ValueError, uni.Columns, 'field1',
                          grid = grid('grid 33-33-33'))
        
    def testHtmlPageForm(self):
        from djpcms.apps.contentedit import HtmlPageForm
        from djpcms.html.layout import grid
        l = HtmlPageForm['layout']
        self.assertTrue(l)
        # the columns are the second child (first is the message holder)
        columns = l.children[1]
        self.assertEqual(columns.grid, grid('grid 33-33-33'))
        w = HtmlPageForm()
        text = w.render()
        self.assertTrue(text)