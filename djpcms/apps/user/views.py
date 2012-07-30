from djpcms import views
from djpcms.cms import HttpRedirect, permissions
from djpcms.cms.formutils import saveform

from .forms import HtmlLoginForm, HtmlLogoutForm

__all__ = ['LogoutView',
           'LoginView']


class LogoutView(views.ModelView):
    '''Logs out a user, if there is an authenticated user :)
    '''
    PERM = permissions.NONE
    ICON = 'logout'
    default_route = 'logout'
    default_title = 'Log out'
    default_link = 'Log out'
    ajax_enabled = True
    DEFAULT_METHOD = 'post'
    form = HtmlLogoutForm

    def post_response(self, request):
        return saveform(request)
    #def __call__(self, request):
    #    params = dict(request.GET.items())
    #    url = params.get('next', None) or '/'
    #    if request.view.permissions.logout(request.environ):
    #        raise HttpRedirect(url)
    #    raise ValueError('Could not logout')


class LoginView(views.ModelView):
    '''A Battery included Login view.
    '''
    ICON = 'login'
    PERM = permissions.NONE
    form = HtmlLoginForm
    has_plugin = True
    redirect_to_view = 'home'
    force_redirect = True
    default_route = 'login'
    default_title = 'Sign in'
    default_link = 'Sign in'
    body_class = 'tiny'

    def __call__(self, request):
        if request.user.is_authenticated():
            raise HttpRedirect('/')
        return super(LoginView, self).__call__(request)

    def render(self, request):
        if request.user.is_authenticated():
            return ''
        else:
            return self.get_form(request).render(request)

    def post_response(self, request):
        return saveform(request, force_redirect=self.force_redirect)

    def has_permission(self, *args, **kwargs):
        return True

