from djpcms import forms, html
from djpcms.utils import test

from .forms import SimpleForm


class TestSimpleForm(test.TestCase):
    '''Test the form library using form in included applications'''
    
    def testSimpleFactory(self):
        self.assertEqual(len(SimpleFodm.base_fields),3)
        form = SimpleForm()
        self.assertFalse(fodm.is_bound)
        self.assertFalse(fodm.is_valid())
        
    def testValidSimpleBound(self):
        prefix = 'sjkdcbksdjcbdf-'
        form = SimpleForm(data = {prefix+'name':'pinco'},
                          prefix = prefix)
        self.assertTrue(fodm.is_bound)
        self.assertTrue(fodm.is_valid())
        self.assertEqual(fodm.cleaned_data['name'],'pinco')
        self.assertTrue(fodm.cleaned_data['age'])
        
    def testSimpleHtml(self):
        hf = forms.HtmlForm(SimpleForm)
        self.assertTrue('action' in hf.attributes)
        self.assertTrue('enctype' in hf.attributes)
        self.assertTrue('method' in hf.attributes)
        self.assertTrue(hf.form_class,SimpleForm)
        w = hf(action = '/test/')
        self.assertTrue(isinstance(w.internal['form'], SimpleForm))
        self.assertEqual(w.attrs['action'],'/test/')
        self.assertEqual(w.attrs['method'],'post')
        
    def testInitial(self):
        hf = forms.HtmlForm(SimpleForm)
        w = hf(initial = {'name':'luca','age':39,'profession':2})\
                    .addAttr('action','/test/')
        text = w.render()
        self.assertTrue('luca' in text)
        self.assertTrue('39' in text)
        
