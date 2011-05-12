from djpcms import test, forms, sites
from djpcms.plugins.apps import HtmlSearchForm
from djpcms.apps.included.contentedit import PageForm, EditContentForm

from .forms import SimpleForm


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
        '''Test the Page Form'''
        d = dict(PageForm.initials())
        self.assertTrue(d)
        p = PageForm()
        self.assertFalse(p.is_bound)
        initial = p.initial
        self.assertEqual(initial['in_navigation'],0)
        self.assertEqual(d,initial)
        
    @test.skipUnless(sites.tests.CMS_ORM,"Testing without ORM")
    def testPageFormBound(self):
        from djpcms.models import Page
        d = dict(PageForm.initials())
        p = PageForm(data = d)
        self.assertFalse(p.is_valid())
        p = PageForm(data = d, model = Page)
        self.assertTrue(p.is_valid())
        page = p.save()
        page = Page.objects.get(id = page.id)
        for k,v in d.items():
            self.assertEqual(getattr(page,k),v)
        p = PageForm(instance = page)
        dp = p.initial
        for k,v in d.items():
            self.assertEqual(dp[k],v)
            
        # Now we test the rendered form
        hf = forms.HtmlForm(PageForm)
        w = hf.widget(p, action = '/test/')
        html = w.render()
        self.assertTrue('value="0"' in html)
        
    def testSearchForm(self):
        '''Test the search form in :mod:`djpcms.plugins.apps`'''
        self.assertTrue(len(HtmlSearchForm.inputs),1)
        s = HtmlSearchForm.inputs[0].render()
        self.assertTrue('<input ' in s)
        self.assertTrue(s.startswith("<div class='cx-submit'>"))
        form = HtmlSearchForm()
        self.assertFalse(form.is_bound)
        widget = HtmlSearchForm.widget(form)
        html = widget.render()
        self.assertTrue(html)
        
    def __testContentEditForm(self):
        form = EditContentForm()
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

