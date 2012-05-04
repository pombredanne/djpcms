import os

from djpcms import forms, html
from djpcms.utils import test
from djpcms.apps.search import search_form
from djpcms.apps.contentedit import HtmlPageForm,\
                                    ContentBlockHtmlForm,\
                                    HtmlEditContentForm
                                    
from . import base
                                    
                                    
class TestSimpleForm(base.TestCase):
    '''Test the form library using form in included applications'''
    
    def page_data(self, layout='default', grid_system = 'fixed_12',
                  inner_template = 'grid 100', **kwargs):
        d = dict(HtmlPageFodm.form_class.initials())
        d['layout'] = layout
        d['grid_system'] = grid_system
        d['inner_template'] = inner_template
        d.update(kwargs)
        return d
        
    def testAddPage(self):
        client = self.create_user_and_login()
        d = self.page_data()
        client.post('/admin/cms/')
        p = HtmlPageForm(data = d)
        form = p.form
        self.assertFalse(fodm.is_valid())
        p = HtmlPageForm(data=d, model=Page)
        self.assertTrue(p.is_valid())
        page = p.fodm.save()
        page = Page.objects.get(id = page.id)
        for k,v in d.items():
            self.assertEqual(getattr(page,k),v)
        p = HtmlPageForm(instance = page)
        dp = p.fodm.initial
        for k,v in d.items():
            self.assertEqual(dp[k],v)
            
        # Now we test the rendered form
        w = p.addAttr('action','/test/')
        html = w.render()
        self.assertTrue('value="0"' in html)