'''Application for static files'''
import djpcms
from djpcms.utils import test


class TestStaticMeta(test.TestCase):
    
    def testStaticApplication(self):
        from djpcms.apps.static import Static
        app = Static('media/')
        self.assertEqual(len(app),2)
        self.assertFalse(app.isbound)
        self.assertEqual(app[0].name,'root')
        self.assertEqual(app[1].name,'path')
        site = djpcms.Site(djpcms.get_settings(APPLICATION_URLS = (app,)))
        site.load()
        self.assertEqual(len(app.urls()),2)
        
    def testFavIcon(self):
        from djpcms.apps.static import FavIconView
        view = FavIconView()
        self.assertEqual(view.path,'/favicon.ico')
        self.assertFalse(view.isbound)