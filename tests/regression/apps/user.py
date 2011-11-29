import djpcms
from djpcms.utils import test


class UserAppMeta(test.TestCase):
    
    def testViews(self):
        from djpcms.apps.user import UserApplication
        app = UserApplication('/accounts/')
        self.assertEqual(len(app),5)
        self.assertFalse(app.isbound)
        self.assertEqual(app[0].name,'home')
        self.assertEqual(app[1].name,'login')
        self.assertEqual(app[2].name,'logout')
        self.assertEqual(app[3].name,'add')
        self.assertEqual(app[4].name,'change_password')
        

@test.skipUnless(test.djpapps,"Requires djpapps installed")
class UserApp(test.TestCase):
    
    def urls(self):
        from djpcms.apps.user import UserApplication
        from sessions.models import User
        return (UserApplication('/accounts/', User),)
    
    def setUp(self):
        settings = djpcms.get_settings(APPLICATION_URLS = self.urls,
                                       INSTALLED_APPS = ('djpcms','sessions'))
        self.site = djpcms.Site(settings)
        
    def testMeta(self):
        '''Check the application meta attributes'''
        site = self.site
        self.assertFalse(site.isbound)
        self.assertEqual(len(site),0)
        urls = self.site.urls()
        self.assertEqual(len(urls),1)
        self.assertTrue(site.isbound)
        
    def testLoginResolver(self):
        view, urlargs = self.site.resolve('accounts/login')
        app = self.site[0]
        self.assertEqual(view,app.views['login'])
        self.assertEqual(urlargs,{})
        
    def testLogoutResolver(self):
        view, urlargs = self.site.resolve('accounts/logout')
        app = self.site[0]
        self.assertEqual(view,app.views['logout'])
        self.assertEqual(urlargs,{})
        
