'''Application for static files'''
from djpcms.utils import test


class TestStaticMeta(test.TestCase):
    
    def testStaticApplication(self):
        from djpcms.apps.static import Static
        app = Static('media/')
        self.assertEqual(len(app),2)
        self.assertFalse(app.isbound)
        self.assertEqual(app[0].name,'root')
        self.assertEqual(app[1].name,'path')
        self.assertEqual(len(app.urls()),2)
        
    def testFavIcon(self):
        from djpcms.apps.static import FavIcon
        app = FavIcon()
        self.assertEqual(len(app),1)
        self.assertFalse(app.isbound)
        self.assertEqual(len(app.urls()),1)