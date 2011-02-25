from djpcms import test, sites
from djpcms.apps.included.user import LoginForm
from djpcms.views import appsite, appview
from djpcms.apps.included.user import UserApplication

from .models import User, installed_apps

# Django user aplication
appurls = UserApplication('/accounts/', User),


class TestUserMixin(test.TestCase):
    appurls = 'regression.user.tests'
    
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
        
    def testLoginForm(self):
        self.assertTrue(len(LoginForm.base_fields),2)
        form = LoginForm()
        self.assertFalse(form.is_bound)
        self.assertFalse(form.is_valid())
        
    def testValidLoginForm(self):
        prefix = 'sjkdcbksdjcbdf-'
        form = LoginForm(data = {prefix+'username':'pinco',
                                 prefix+'password':'blabla'},
                         prefix = prefix)
        self.assertTrue(form.is_bound)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.data['username'],'pinco')
        self.assertEqual(form.data['password'],'blabla')
        

