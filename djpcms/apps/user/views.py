from djpcms import views, http
from djpcms.forms.utils import saveform

__all__ = ['LogoutView','LoginView','UserView','UserDataView']



class LogoutView(views.ModelView):
    '''Logs out a user, if there is an authenticated user :)
    '''
    default_route = 'logout'
    default_title = 'Log out'
    default_link = 'Log out'
    
    def __call__(self, request):
        params  = dict(request.GET.items())
        url     = params.get('next',None) or '/'
        backend = request.view.permissions.backend
        if backend:
            backend.logout(request.environ)
            return http.ResponseRedirect(url)
        else:
            raise ValueError('No athentication backend available')



class LoginView(views.ModelView):
    '''A Battery included Login view. You need to
    create a login.html file in your site template directory.
    '''
    has_plugin = True
    default_route = 'login'
    default_title = 'Sign in'
    default_link = 'Sign in'
    template_name = ('login.html','djpcms/tiny.html')
    
    def __call__(self, request):
        if request.user.is_authenticated():
            return http.ResponseRedirect('/')
        return super(LoginView,self).__call__(request)
        
    def render(self, request):
        if request.user.is_authenticated():
            return ''
        else:
            return self.get_form(request).render(request)
    
    def default_post(self, request):
        return saveform(request, force_redirect = self.force_redirect)
    
    def success_message(self, instance, mch):
        return ''
    
    def has_permission(self, *args, **kwargs):
        return True


class UserView(views.ViewView):
    
    def title(self, request):
        return request.instance.username
            
            
class UserDataView(UserView):
    
    def render(self, request):
        return ''
    