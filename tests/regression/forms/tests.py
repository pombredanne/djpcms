from djpcms import test, forms
from djpcms.apps.included.contentedit.forms import PageForm
from .forms import SimpleForm


class TestSimpleForm(test.TestCase):
    
    def testSimpleFactory(self):
        self.assertTrue(len(SimpleForm.base_fields),2)
        form = SimpleForm()
        self.assertFalse(form.is_bound)
        self.assertFalse(form.is_valid())
        
    def testValidSimpleBound(self):
        prefix = 'sjkdcbksdjcbdf-'
        form = SimpleForm(data = {prefix+'name':'pinco'},
                          prefix = prefix)
        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.data['name'],'pinco')
        self.assertTrue(form.data['age'])
        
    def testSimpleHtml(self):
        hf = forms.HtmlForm(SimpleForm)
        self.assertTrue(hf.form_class,SimpleForm)
        w = hf.widget(hf.form_class(), action = '/test/')
        self.assertTrue(isinstance(w.form,SimpleForm))
        self.assertEqual(w.attrs['action'],'/test/')
        self.assertEqual(w.attrs['method'],'post')
        
    def testInitial(self):
        f = SimpleForm(initial = {'name':'luca','age':39,'profession':2})
        hf = forms.HtmlForm(SimpleForm)
        w = hf.widget(f, action = '/test/')
        html = w.render()
        self.assertTrue('luca' in html)
        self.assertTrue('39' in html)
        
    def testPageForm(self):
        d = dict(PageForm.initials())
        self.assertTrue(d)
        p = PageForm()
        self.assertFalse(p.is_bound)
        initial = p.initial
        self.assertEqual(initial['in_navigation'],1)
        self.assertEqual(d,initial)
        
