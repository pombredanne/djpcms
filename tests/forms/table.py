'''Test form table layouts'''
from djpcms.utils import test

class TestTableLayout(test.TestCase):

    def form(self):
        '''Build the form and the form layout'''
        from djpcms import forms
        from djpcms.forms import layout as uni

        class testForm(forms.Form):
            entry1__color = forms.CharField()
            entry1__size = forms.IntegerField()
            entry2__color = forms.CharField()
            entry2__size = forms.IntegerField()
            entry3__color = forms.CharField()
            entry3__size = forms.IntegerField()

        return forms.HtmlForm(testForm,
                    layout=uni.FormLayout(
                        uni.TableFormElement(('entry', 'color', 'size'),
                                             ('entry1', 'entry1__color', 'entry1__size'),
                                             ('entry2', 'entry2__color', 'entry2__size'),
                                             ('entry3', 'entry3__color', 'entry3__size'),
                                             key='table',
                                             legend='Leggenda')))

    def __testFieldlist(self):
        '''Test the field list class'''
        # The field list class is useful for constructing forms

    def testFormClass(self):
        html = self.form()
        self.assertTrue(html.form_class)
        self.assertEqual(len(html.form_class.base_fields), 6)
        table = html['layout']['table']
        self.assertEqual(len(table.fields), 3)
        self.assertEqual(len(table.headers), 3)
        self.assertEqual(len(table.children), 4)
        # The first child is the legend
        children = list(table.allchildren())
        row1 = children[1]
        self.assertEqual(len(row1.children),3)

    def testForm(self):
        html = self.form()()
        self.assertTrue(html.form)
        self.assertFalse(html.form.is_bound)
        text = html.render()
        self.assertTrue('<table' in text)
        self.assertTrue('<thead>' in text)
        self.assertTrue('</thead>' in text)
        self.assertTrue('<tbody>' in text)
        self.assertTrue('</tbody>' in text)
