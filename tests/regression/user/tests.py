from djpcms import test, sites
from djpcms.apps.included.user import LoginForm
from djpcms.views import appsite, appview
from djpcms.apps.included.vanilla import Application
from djpcms.apps.included.user import UserApplication, UserSite


def appurls2():
    from .models import User, Portfolio
    apps = (Application('/portfolio/', Portfolio,
                        parent = 'userhome'),)
    return (UserSite('/', User, apps = apps),)


@test.skipUnless(sites.tests.CMS_ORM,"Testing without ORM")
class TestSiteUser(test.TestCase, test.UserMixin):
    appurls = 'regression.user.tests.appurls2'
    
    def setUp(self):
        from .models import User, Portfolio
        self.User = User
        self.Portfolio = Portfolio
        self.makesite()
        self.sites.load()
        self.makeusers()
        
    def installed_apps(self):
        from .models import installed_apps
        return []
        
    def testApps(self):
        app = self.sites.for_model(self.User)
        site = app.site
        self.assertTrue(len(site),2)
        views = app.views
        self.assertEqual(len(views),4)
        urls = app._urls
        self.assertEqual(len(urls),4)
        apps = app.apps
        self.assertEqual(len(apps),1)
        papp = apps['portfolio']
        self.assertEqual(len(papp.views),5)
        self.assertEqual(len(papp._urls),5)
        
    def testHomePage(self):
        response = self.get()
        info = response.DJPCMS
        self.assertEqual(info.view.model,self.User)
        
    def testUserpage(self):
        response = self.get('/testuser/')
        info = response.DJPCMS
        self.assertEqual(info.instance.username,'testuser')
        response = self.get('/xxxxxxxx/', status = 404)
        
    def testUserApplication(self):
        response = self.get('/testuser/portfolio/')
        info = response.DJPCMS
        self.assertEqual(info.instance,None)
        
    def _testlogin(self, user, ajax = True):
        url = '/accounts/login/'
        context = self.get(url)
        uni = context['uniform']
        self.assertTrue(uni)
        data = {'username':user.username,
                'password':user.password}
        res = self.post(url, data = data, ajax = ajax, response = True)
             
    def __testLoginView(self):
        self._testlogin(self.user)
        
    def _testLoginForm(self):
        self.assertTrue(len(LoginForm.base_fields),2)
        form = LoginForm()
        self.assertFalse(form.is_bound)
        self.assertFalse(form.is_valid())
        
    def _testValidLoginForm(self):
        prefix = 'sjkdcbksdjcbdf-'
        form = LoginForm(data = {prefix+'username':'pinco',
                                 prefix+'password':'blabla'},
                         prefix = prefix)
        self.assertTrue(form.is_bound)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.data['username'],'pinco')
        self.assertEqual(form.data['password'],'blabla')
        

