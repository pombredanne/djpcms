'''Content edit application and forms'''
import os
from djpcms.utils import test

@test.skipUnless(os.environ['stdcms'], 'Requires stdcms installed')
class ContentEditApplication(test.TestCaseWidthAdmin):
    installed_apps = ('stdcms', 'stdcms.cms', 'djpcms.apps.contentedit')
    
    def page_data(self, layout='default', grid_system = 'fixed_12',
                  inner_template = 'grid 100', **kwargs):
        from djpcms.apps.contentedit import HtmlPageForm
        d = dict(HtmlPageForm.form_class.initials())
        d['layout'] = layout
        d['grid_system'] = grid_system
        d['inner_template'] = inner_template
        d.update(kwargs)
        return d
        
    def testBlockApplication(self):
        site = self.site()
        self.assertTrue(site.BlockContent)
        app = site.for_model(site.BlockContent)
        self.assertEqual(len(app), 4)
        
    def testInitialPageForm(self):
        '''Test the Page Form'''
        from djpcms.apps.contentedit import HtmlPageForm
        d = dict(HtmlPageForm.form_class.initials())
        self.assertTrue(d)
        ph = HtmlPageForm()
        p = ph.form
        self.assertFalse(p.is_bound)
        initial = p.initial
        self.assertEqual(initial['in_navigation'],0)
        self.assertEqual(d,initial)
        
    def testPageFormBound(self):
        from djpcms.apps.contentedit import HtmlPageForm
        from stdcms.cms.models import Page
        from stdnet import odm
        d = self.page_data()
        p = HtmlPageForm(data=d)
        form = p.form
        self.assertFalse(p.is_valid())
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
        
    def testBlockForm(self):
        from djpcms.apps.contentedit import ContentBlockHtmlForm
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

            