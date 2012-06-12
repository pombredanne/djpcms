import os

from djpcms import forms, html
from djpcms.utils import test
from djpcms.apps.search import search_form
from djpcms.apps.contentedit import HtmlPageForm,\
                                    ContentBlockHtmlForm,\
                                    HtmlEditContentForm
                                    
                                    
class TestSimpleForm(test.TestCase):
    '''Test the form library using form in included applications'''
    
    def page_data(self, layout='default', grid_system = 'fixed_12',
                  inner_template = 'grid 100', **kwargs):
        d = dict(HtmlPageForm.form_class.initials())
        d['layout'] = layout
        d['grid_system'] = grid_system
        d['inner_template'] = inner_template
        d.update(kwargs)
        return d
        
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
        from stdnet import odm
        odm.register(Page)
        d = self.page_data()
        p = HtmlPageForm(data = d)
        form = p.form
        self.assertFalse(form.is_valid())
        p = HtmlPageForm(data=d, model=Page)
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
        self.assertTrue(len(fw.children),1)
        layout = fw['layout']
        self.assertTrue(layout.children)
        plugin = layout.children['plugin']
        self.assertTrue(plugin.classes)
        self.assertEqual(plugin.tag, 'div')
        text = fw.render()
        self.assertTrue(text)
        self.assertTrue(plugin.maker.default_style in text)
        
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

        

