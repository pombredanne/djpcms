from djpcms.views import appsite, appview
from djpcms.forms import HtmlForm

from .forms import LoginForm, PasswordChangeForm, RegisterForm
from .views import *

permission = lambda self, request, obj: False if not request else request.user.is_authenticated()


class UserApplication(appsite.ModelApplication):
    '''This is a special Application since it deals with users and therefore is everywhere.
No assumption has been taken over which model is used for storing user data.'''
    name     = 'account'
    userpage = False
    form     = PasswordChangeForm
    
    home   = appview.ModelView()
    login  = LoginView(parent = 'home', form = HtmlForm(LoginForm, submits = (('Sign in','login_user'),)))
    logout = LogoutView(parent = 'home')
    change = appview.EditView(regex = 'change',
                              isplugin = True,
                              parent = 'home',
                              form = HtmlForm(PasswordChangeForm))
    add = appview.AddView(regex = 'create',
                          isplugin = True,
                          parent = 'home',
                          form = HtmlForm(RegisterForm,
                                          submits = (('Create','create_user'),)),
                          force_redirect = True)
    
    def registration_done(self):
        '''Set the user model in the application site'''
        self.application_site.User = self.mapper
    
    def objectbits(self, obj):
        if self.userpage:
            return {'username': obj.username}
        else:
            return {}
    
    def get_object(self, request, *args, **kwargs):
        if self.userpage:
            try:
                username = kwargs.get('username',None)
                return self.model.objects.get(username = username)
            except:
                return None
        else:
            return request.user
        
    def has_add_permission(self, request = None, obj = None):
        if request:
            if not request.user.is_authenticated():
                return True
        return False
    
    def has_edit_permission(self, request = None, obj=None):
        return permission(self,request,obj)
    