from djpcms import test, forms, sites, html
from djpcms.plugins.apps import HtmlSearchForm
from djpcms.apps.included.contentedit import HtmlPageForm,\
                                             ContentBlockHtmlForm,\
                                             HtmlEditContentForm
from djpcms.apps.included.contactus import ContactForm

from .forms import SimpleForm


def dummy_send(*args,**kwargs):
    pass


class TestSimpleForm(test.TestCase):
    '''Test the form library using form in included applications'''
    
    def testSimpleFactory(self):
        self.assertEqual(len(SimpleForm.base_fields),3)
        form = SimpleForm()
        self.assertFalse(form.is_bound)
        self.assertFalse(form.is_valid())
        
    def testValidSimpleBound(self):
        prefix = 'sjkdcbksdjcbdf-'
        form = SimpleForm(data = {prefix+'name':'pinco'},
                          prefix = prefix)
        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['name'],'pinco')
        self.assertTrue(form.cleaned_data['age'])
        
    def testSimpleHtml(self):
        hf = forms.HtmlForm(SimpleForm)
        self.assertTrue('action' in hf.attributes)
        self.assertTrue('enctype' in hf.attributes)
        self.assertTrue('method' in hf.attributes)
        self.assertTrue(hf.form_class,SimpleForm)
        w = hf.widget(form = hf.form_class(), action = '/test/')
        self.assertTrue(isinstance(w.form,SimpleForm))
        self.assertEqual(w.attrs['action'],'/test/')
        self.assertEqual(w.attrs['method'],'post')
        
    def testInitial(self):
        hf = forms.HtmlForm(SimpleForm)
        w = hf(initial = {'name':'luca','age':39,'profession':2}).addAttr('action','/test/')
        text = w.render()
        self.assertTrue('luca' in text)
        self.assertTrue('39' in text)
        
    def testPageForm(self):
        '''Test the Page Form'''
        d = dict(HtmlPageForm.form_class.initials())
        self.assertTrue(d)
        ph = HtmlPageForm()
        p = ph.form
        self.assertFalse(p.is_bound)
        initial = p.initial
        self.assertEqual(initial['in_navigation'],0)
        self.assertEqual(d,initial)
        
    @test.skipUnless(sites.tests.CMS_ORM,"Testing without ORM")
    def testPageFormBound(self):
        from djpcms.models import Page
        d = dict(HtmlPageForm.form_class.initials())
        p = HtmlPageForm(data = d)
        self.assertFalse(p.is_valid())
        p = HtmlPageForm(data = d, model = Page)
        self.assertTrue(p.is_valid())
        page = p.form.save()
        page = Page.objects.get(id = page.id)
        for k,v in d.items():
            self.assertEqual(getattr(page,k),v)
        p = HtmlPageForm(instance = page)
        dp = p.form.initial
        for k,v in d.items():
            self.assertEqual(dp[k],v)
            
        # Now we test the rendered form
        w = p.addAttr('action','/test/')
        html = w.render()
        self.assertTrue('value="0"' in html)
        
    def testSearchForm(self):
        '''Test the search form in :mod:`djpcms.plugins.apps`'''
        self.assertTrue(len(HtmlSearchForm.inputs),1)
        s = HtmlSearchForm.inputs[0].render()
        self.assertTrue('<input ' in s)
        self.assertTrue(s.startswith("<div class='cx-submit'>"))
        w = HtmlSearchForm()
        form = w.form
        self.assertFalse(form.is_bound)
        html = w.render()
        self.assertTrue(html)
        
    def testBlockForm(self):
        fw = ContentBlockHtmlForm()
        form = fw.form
        self.assertFalse(form.is_bound)
        self.assertTrue(fw.layout.children)
        self.assertTrue(len(fw.layout.children),1)
        plugin = fw.layout.children['plugin']
        self.assertTrue(isinstance(plugin,html.WidgetMaker))
        self.assertTrue(plugin.default_class)
        self.assertEqual(plugin.tag,'div')
        text = fw.render()
        self.assertTrue(text)
        self.assertTrue(plugin.default_class in text)
        
    def __testContentEditForm(self):
        fw = HtmlEditContentForm()
        form = fw.form
        self.assertFalse(form.is_bound)
        #
        # Test the markup field
        bmarkup = form.dfields['markup'] # markup bound field
        markup = bmarkup.field
        self.assertTrue(markup.choices)
        self.assertEqual(markup.empty_label,None)
        self.assertTrue(markup.separator)
        choices,model = markup.choices_and_model(bmarkup)
        self.assertEqual(model,None)
        self.assertTrue(choices)
        self.assertEqual(choices[0][0],'')
        self.assertEqual(choices[0][1],'raw')


class TestFormValidation(test.TestCase):
    
    def testContantForm(self):
        d = ContactForm(data = {'body':'blabla'}, send_message = dummy_send)
        self.assertFalse(d.is_valid())
        self.assertEqual(len(d.errors),2)
        self.assertEqual(d.errors['name'], ['name is required'])
        self.assertEqual(d.errors['email'], ['email is required'])
        d = ContactForm(data = {'body':'blabla','name':''}, send_message = dummy_send)
        self.assertFalse(d.is_valid())
        self.assertEqual(len(d.errors),2)
        self.assertTrue('name' in d.errors)
        d = ContactForm(data = {'body':'blabla','name':'pippo','email':'pippo@pippo.com'},
                        send_message = dummy_send)
        self.assertTrue(d.is_valid())
