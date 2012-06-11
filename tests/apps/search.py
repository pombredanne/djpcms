'''Application for searching models.'''
from djpcms import cms
from djpcms.utils import test


class DummyEngine(object):
    
    def search(self, text, include = None):
        return ()


class TestSearchMeta(test.TestCase):
    
    def testSearchApplication(self):
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
        