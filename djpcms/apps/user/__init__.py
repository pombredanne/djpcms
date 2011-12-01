'''\
Dependencies: a **User model** from an external library.

For example, lets say you want to use ``django.contrib.auth``
as your user model, than you can define the application::

    from django.contrib.auth.models import User
    from djpcms.apps.user import UserApplication
    
    UserApplication('/accounts/',User)
     
'''

from djpcms.forms import HtmlForm

from .forms import LoginForm, PasswordChangeForm, RegisterForm, UserChangeForm
from .views import *

from djpcms import views

permission = lambda self, request, obj: False if not request \
                else request.user.is_authenticated()


class UserAppBase(views.Application):
    '''Base class for user applications. Defines several
utility methods for dealing with users and user data.'''
    name = 'accounts'
    userpage = False
    home = views.SearchView()
    login = LoginView(template_file = ('login.html','djpcms/login.html'),
                      inherit_page = False,
                      form = HtmlForm(LoginForm,
                                      inputs = (('Sign in','login_user'),)))
    logout = LogoutView()
    add = views.AddView(in_nav = 0,
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
        
    def on_bound(self):
        '''Set the user model in the application site'''
        self.root.internals['User'] = self.mapper
    
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
    inherit = True
    in_nav = 0  
    change_password = views.ChangeView('change-password',
                                       has_plugins = True,
                                       parent_view = 'home',
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
    userhome = UserView('<username>/')
    change  = views.ChangeView(parent_view = 'userhome',
                               form = HtmlForm(UserChangeForm))
    change_password = views.ChangeView('change-password',
                                       parent_view = 'userhome',
                                       has_plugins = True,
                                       form = HtmlForm(PasswordChangeForm))
    #userdata = UserDataView('(?P<path>[\w./-]*)',
    #                        parent_view = 'userhome')
    
    def for_user(self, djp):
        '''If user instance not available, return None'''
        try:
            return djp.instance
        except djp.http.Http404:
            return None
    
    def get_view_from_path(self, path):
        path = path.split('/')
        

class UserDataApplication(views.Application):
    pass

