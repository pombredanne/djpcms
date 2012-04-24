'''\
Dependencies: a **User model** from an external library.

For example, lets say you want to use ``django.contrib.auth``
as your user model, than you can define the application::

    from django.contrib.auth.models import User
    from djpcms.apps.user import UserApplication
    
    UserApplication('/accounts/',User)
     
'''

from djpcms.forms import HtmlForm

from .forms import LoginForm, HtmlRegisterForm, \
                    UserChangeForm, HtmlLoginForm, HtmlChangePassword
from .views import *

from djpcms import views

permission = lambda self, request, obj: False if not request \
                else request.user.is_authenticated()


class UserAppBase(views.Application):
    '''Base class for user applications. Defines several
utility methods for dealing with users and user data.'''
    name = 'accounts'
    userpage = False
    exclude_links = ('login','logout')
    
    home = views.SearchView()
    login = LoginView()
    logout = LogoutView()
    add = views.AddView(in_nav = 0,
                        form = HtmlRegisterForm,
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
        
    def instance_from_variables(self, environ, urlargs):
        if self.userpage:
            return super(UserAppBase,self).instance_from_variables(environ,
                                                                   urlargs)
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
                                       form = HtmlChangePassword)
        
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
                                       form = HtmlChangePassword)
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

