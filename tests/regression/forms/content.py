import os

from djpcms import forms, html
from djpcms.utils import test
from djpcms.apps.search import search_form
from djpcms.apps.contentedit import HtmlPageForm,\
                                    ContentBlockHtmlForm,\
                                    HtmlEditContentForm
                                    
                                    
class TestSimpleForm(test.TestCase):
    '''Test the form library using form in included applications'''
    
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
        
    @test.skipUnless(os.environ['stdcms'], "Requires stdcms installed")
    def testPageFormBound(self):
        from stdcms.cms.models import Page
        from stdnet import orm
        orm.register(Page)
        d = dict(HtmlPageForm.form_class.initials())
        p = HtmlPageForm(data = d)
        form = p.internal['form']
        self.assertFalse(form.is_valid())
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
        HtmlSearchForm = search_form()
        self.assertEqual(len(HtmlSearchForm.inputs),0)
        w = HtmlSearchForm()
        form = w.internal['form']
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

        

