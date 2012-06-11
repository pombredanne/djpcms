'''Application for static files'''
import djpcms
from djpcms.utils import test


class TestStaticMeta(test.TestCase):
    
    def urls(self, site):
        from djpcms.apps.static import Static
        return (Static('media/'),)
    
    def testStaticApplication(self):
        site = self.website()()
        app = site[0]
        self.assertEqual(app.path,'/media/')
        self.assertEqual(len(app),2)
        self.assertEqual(app[0].name,'root')
        self.assertEqual(app[1].name,'path')
        self.assertEqual(len(app.urls()),2)
        
    def testFavIcon(self):
        from djpcms.apps.static import FavIconView
        view = FavIconView()
        self.assertEqual(view.path,'/favicon.ico')
        self.assertFalse(view.isbound)