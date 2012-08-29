'''Application for searching models.'''
from djpcms.utils import test


class DummyEngine(object):
    
    def search(self, text, include = None):
        return ()


class TestSearchMeta(test.TestCase):
    
    def testSearchApplication(self):
        from djpcms import cms
        from djpcms.apps import search
        engine = DummyEngine()
        app = search.Application('search/', engine = engine)
        self.assertTrue(app.forallsites)
        self.assertEqual(app.engine,engine)
        site = cms.Site()
        site.routes.append(app)
        self.assertFalse(site.isbound)
        self.assertEqual(site.search_engine,None)
        self.assertEqual(len(site.urls()),1)
        self.assertEqual(site.search_engine,app)
        self.assertEqual(site.search_engine.engine,engine)
        
    def testSearchForm(self):
        '''Test the search form in :mod:`djpcms.plugins.apps`'''
        from djpcms.apps import search
        HtmlSearchForm = search.search_form()
        self.assertEqual(len(HtmlSearchForm.inputs),0)
        w = HtmlSearchForm()
        form = w.internal['form']
        self.assertFalse(form.is_bound)
        html = w.render()
        self.assertTrue(html)
        