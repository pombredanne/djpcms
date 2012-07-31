from djpcms import views
from djpcms.cms import HttpRedirect, permissions

from .forms import HtmlLoginForm, HtmlLogoutForm

__all__ = ['LogoutView',
           'LoginView']


class LoginLogout(views.AddView):
    PERM = permissions.NONE
    force_redirect = True


class LogoutView(LoginLogout):
    '''Log out a user, via a POST request'''
    ICON = 'logout'
    default_route = 'logout'
    default_title = 'Log out'
    default_link = 'Log out'
    ajax_enabled = True
    has_plugins = False
    DEFAULT_METHOD = 'post'
    form = HtmlLogoutForm

    def __call__(self, request):
        if not request.user.is_authenticated():
            raise HttpRedirect('/')
        return super(LogoutView, self).__call__(request)


class LoginView(LoginLogout):
    '''A Battery included Login view.
    '''
    ICON = 'login'
    form = HtmlLoginForm
    has_plugins = True
    default_route = 'login'
    default_title = 'Sign in'
    default_link = 'Sign in'

    def __call__(self, request):
        if request.user.is_authenticated():
            raise HttpRedirect('/')
        return super(LoginView, self).__call__(request)

    def render(self, request, **kwargs):
        if request.user.is_authenticated():
            return ''
        else:
            return super(LoginView, self).render(request, **kwargs)

