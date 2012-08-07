'''\
Dependencies: a **User model** from an external library.

For example, lets say you want to use ``django.contrib.auth``
as your user model, than you can define the application::

    from django.contrib.auth.models import User
    from djpcms.apps.user import UserApplication

    UserApplication('/accounts/',User)

'''
from .forms import *
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
    #
    home = views.SearchView()
    login = LoginView(in_nav=0)
    logout = LogoutView(in_nav=0)
    add = views.AddView(in_nav=0,
                        form=HtmlAddUserForm,
                        force_redirect=True)
    register = views.AddView('/register',
                             in_nav=0,
                             linkname=lambda r: 'register',
                             form=HtmlRegisterForm,
                             force_redirect=True)

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


class UserApplication(UserAppBase):
    '''This is a special Application since it deals with users and therefore is everywhere.
No assumption has been taken over which model is used for storing user data.'''
    in_nav = 0
    view = views.ViewView('<username>/')
    change = views.ChangeView(form=HtmlUserChangeForm)
    change_password = views.ChangeView('change-password',
                                       linkname=lambda r: 'change password',
                                       icon='icon-key',
                                       has_plugins=True,
                                       form=HtmlChangePassword)
