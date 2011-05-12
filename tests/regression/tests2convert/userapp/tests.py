from djpcms import test, sites
from djpcms.apps.included.user import LoginForm
from djpcms.views import appsite, appview
from djpcms.apps.included.vanilla import Application
from djpcms.apps.included.user import UserApplication, UserApplicationWithFilter

USER_NUMVIEWS = 6

class CustomUserApp(UserApplicationWithFilter):
    inherit = True


# A web site with user pages
def appurls1():
    from .models import User, Portfolio
    apps = (Application('/portfolio/', Portfolio,
                        parent = 'userhome'),)
    return (CustomUserApp('/',
                          User, apps = apps),
            )


# A web site with user pages
def appurls2():
    from .models import User, Portfolio
    apps = (Application('/portfolio/', Portfolio,
                         parent = 'userhome'),)
    return (UserApplication('/',User, apps = apps),
            )
    

@test.skipUnless(sites.tests.CMS_ORM,"Testing without ORM")
class TestSiteUser1(test.TestCase, test.UserMixin):
    appurls = 'regression.userapp.tests.appurls1'
    NUMVIEWS = USER_NUMVIEWS
    
    def setUp(self):
        from .models import User, Portfolio
        self.User = User
        self.Portfolio = Portfolio
        self.makesite()
        self.sites.load()
        self.makeusers()
        
    def installed_apps(self):
        from .models import installed_apps
        return installed_apps
        
    def testMeta(self):
        views = CustomUserApp.base_views
        self.assertEqual(len(views),self.NUMVIEWS)
        
    def testAppsViews(self):
        app = self.sites.for_model(self.User)
        site = app.site
        self.assertTrue(len(site),2)
        views = app.views
        self.assertEqual(len(views),self.NUMVIEWS)
        urls = app._urls
        self.assertEqual(len(urls),self.NUMVIEWS)
        apps = app.apps
        self.assertEqual(len(apps),1)
        # Get the vanilla portfolio application
        papp = apps['portfolio']
        self.assertEqual(len(papp.views),5)
        self.assertEqual(len(papp._urls),5)
        
    def testUserApplications(self):
        port_app = self.sites.for_model(self.Portfolio)
        user_app = self.sites.for_model(self.User)
        self.assertTrue(port_app.parent)
        self.assertEqual(port_app.parent,user_app.getview('userhome'))
        
    def testHomePage(self):
        response = self.get()
        info = response.DJPCMS
        self.assertEqual(info.view.model,self.User)
        
    def testUserpage(self):
        response = self.get('/testuser/')
        info = response.DJPCMS
        djp = info.djp(response.request)
        self.assertEqual(djp.url,'/testuser/')
        self.assertEqual(info.instance.username,'testuser')
        response = self.get('/xxxxxxxx/', status = 404)
        
    def testUserApplication(self):
        response = self.get('/testuser/portfolio/')
        context = response.context
        info = response.DJPCMS
        djp = info.djp(response.request)
        user = djp.for_user()
        self.assertTrue(user)
        self.assertEqual(user.username,'testuser')
        self.assertEqual(info.instance,None)
        
    def testUserApplicationWithInstance(self):
        p = self.Portfolio(user = self.superuser, name = 'testp', description = 'bla bla')
        p.save()
        response = self.get('/testuser/portfolio/{0}/'.format(p.id))
        context = response.context
        info = response.DJPCMS
        djp = info.djp(response.request)
        user = djp.for_user()
        self.assertTrue(user)
        self.assertEqual(user,self.superuser)
        self.assertEqual(info.instance,p)
        
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
        

#@test.skipUnless(sites.tests.CMS_ORM,"Testing without ORM")
#class TestSiteUser2(TestSiteUser1):
#    appurls = 'regression.userapp.tests.appurls2'
#    NUMVIEWS = USER_NUMVIEWS - 1
