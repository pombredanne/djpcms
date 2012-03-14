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
        

@test.skipUnless(test.djpapps, "Requires djpapps installed")
class UserApp(test.TestCase):
    installed_apps = ('djpcms','sessions')
    
    def urls(self, site):
        from djpcms.apps.user import UserApplication
        from sessions.models import User
        return (UserApplication('/accounts/', User),)
        
    def testMeta(self):
        '''Check the application meta attributes'''
        from sessions.models import User
        site = self.website()()
        self.assertTrue(site.isbound)
        self.assertEqual(site.User.model, User)
        self.assertEqual(len(site),1)
        
    def testLoginResolver(self):
        site = self.website()()
        view, urlargs = site.resolve('accounts/login')
        app = site[0]
        self.assertEqual(view, app.views['login'])
        self.assertEqual(urlargs,{})
        
    def testLogoutResolver(self):
        site = self.website()()
        view, urlargs = site.resolve('accounts/logout')
        app = site[0]
        self.assertEqual(view,app.views['logout'])
        self.assertEqual(urlargs,{})
        
