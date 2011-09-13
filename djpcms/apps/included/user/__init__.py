'''\
Dependencies: a **User model** from an external library.

For example, lets say you want to use ``django.contrib.auth``
as your user model, than you can define the application::

    from django.contrib.auth.models import User
    from djpcms.apps.included.user import UserApplication
    
    UserApplication('/accounts/',User)
     
'''

from djpcms.forms import HtmlForm

from .forms import LoginForm, PasswordChangeForm, RegisterForm, UserChangeForm
from .views import *

from djpcms import views

permission = lambda self, request, obj: False if not request \
                else request.user.is_authenticated()


class UserAppBase(views.ModelApplication):
    '''Base class for user application. Defines several
utility methods for dealing with users and user data.'''
    userpage = False
    home = views.SearchView()
    login = LoginView(template_name = 'login.html',
                      inherit_page = False,
                      form = HtmlForm(LoginForm,
                                      inputs = (('Sign in','login_user'),)))
    logout = LogoutView()
    add = views.AddView(in_navigation = 0,
                        form = HtmlForm(RegisterForm,
                                        inputs = (('Create','create_user'),)),
                        force_redirect = True)
    
    def userhomeurl(self, request):
        '''The user home page url'''
        user = getattr(request,'user',None)
        if user and user.is_authenticated():
            if self.userpage:
                view = self.getview('userhome')
            else:
                view = self.getview('home')
            if view:
                djp = view(request, instance = user)
                return djp.url
        
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
    name    = 'account'
    inherit = True    
    change_password = views.ChangeView(regex = 'change-password',
                                       in_navigation = 0,
                                       isplugin = True,
                                       parent = 'home',
                                       form = HtmlForm(PasswordChangeForm))
        
    def has_add_permission(self, request = None, obj = None):
        # Add new user permissions
        if request:
            if request.user.is_authenticated():
                return True
        return False
    
    def has_edit_permission(self, request = None, obj=None):
        return permission(self,request,obj)


class UserApplicationWithFilter(UserApplication):
    '''Application for managing user home pages in the form of "/username/...".
The userhome view'''
    inherit = True
    userpage = True
    userhome = UserView(regex = '(?P<username>%s)'%views.SLUG_REGEX,
                        description = 'view')
    change  = views.ChangeView(parent = 'userhome',
                               form = HtmlForm(UserChangeForm))
    change_password = views.ChangeView(regex = 'change-password',
                                       parent = 'userhome',
                                       isplugin = True,
                                       form = HtmlForm(PasswordChangeForm))
    #userdata = UserDataView(regex = '(?P<path>[\w./-]*)',
    #                        parent = 'userhome')
    
    def for_user(self, djp):
        '''If user instance not available, return None'''
        try:
            return djp.instance
        except djp.http.Http404:
            return None
    
    def get_view_from_path(self, path):
        path = path.split('/')
        

class UserDataApplication(views.ModelApplication):
    pass

