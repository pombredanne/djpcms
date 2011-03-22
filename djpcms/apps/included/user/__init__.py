'''\
Dependencies: a **User model** from an external library.

For example, lets say you want to use ``django.contrib.auth``
as your user model, than you can define the application::

    from django.contrib.auth.models import User
    from djpcms.apps.included.user import UserApplication
    
    UserApplication('/accounts/',User)
     
'''

from djpcms.forms import HtmlForm

from .forms import LoginForm, PasswordChangeForm, RegisterForm
from .orm import *
from .views import *

from djpcms import views

permission = lambda self, request, obj: False if not request else request.user.is_authenticated()


class UserAppBase(views.ModelApplication):
    userpage = False
    
    def registration_done(self):
        '''Set the user model in the application site'''
        self.site.User = self.mapper
    
    def objectbits(self, obj):
        if self.userpage and isinstance(obj,self.model):
            return {'username': obj.username}
        else:
            return {}
        
    def get_object(self, request, *args, **kwargs):
        if self.userpage:
            try:
                username = kwargs.get('username',None)
                return self.mapper.get(username = username)
            except:
                return None
        else:
            return request.user


class UserApplication(UserAppBase):
    '''This is a special Application since it deals with users and therefore is everywhere.
No assumption has been taken over which model is used for storing user data.'''
    name     = 'account'
    
    home   = views.ModelView()
    login  = LoginView(parent = 'home',
                       template_name = 'login.html',
                       inherit_page = False,
                       form = HtmlForm(LoginForm, submits = (('Sign in','login_user'),)))
    logout = LogoutView(parent = 'home')
    change = views.ChangeView(regex = 'change',
                              isplugin = True,
                              parent = 'home',
                              form = HtmlForm(PasswordChangeForm))
    add = views.AddView(regex = 'create',
                          isplugin = True,
                          parent = 'home',
                          form = HtmlForm(RegisterForm,
                                          submits = (('Create','create_user'),)),
                          force_redirect = True)
        
    def has_add_permission(self, request = None, obj = None):
        if request:
            if not request.user.is_authenticated():
                return True
        return False
    
    def has_edit_permission(self, request = None, obj=None):
        return permission(self,request,obj)


class UserSite(UserAppBase):
    '''Application for managing user home pages in the form of "/username/...".
The userhome view'''
    userpage = True
    home = views.SearchView()
    userhome = views.ViewView(regex = '(?P<username>%s)'%views.SLUG_REGEX,
                              parent = 'home')
    login  = LoginView(parent = 'home',
                       template_name = 'login.html',
                       inherit_page = False,
                       form = HtmlForm(LoginForm, submits = (('Sign in','login_user'),)))
    logout = LogoutView(parent = 'home')
    
    def for_user(self, djp):
        return djp.instance
