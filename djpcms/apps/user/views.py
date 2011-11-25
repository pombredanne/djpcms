from djpcms import views, http
from djpcms.forms.utils import saveform

__all__ = ['LogoutView','LoginView','UserView','UserDataView']



class LogoutView(views.ModelView):
    '''Logs out a user, if there is an authenticated user :)
    '''
    route = 'logout'
        
    def preprocess(self, djp):
        request = djp.request
        params  = dict(request.GET.items())
        url     = params.get('next',None) or '/'
        backend = djp.site.permissions.backend
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
    route = 'login'
    default_title = 'Sign in'
    template_name = 'login.html'
    
    def preprocess(self, djp):
        if djp.request.user.is_authenticated():
            return http.ResponseRedirect('/')
        
    def render(self, djp):
        if djp.request.user.is_authenticated():
            return ''
        else:
            return self.get_form(djp).render(djp)
    
    def default_post(self, djp):
        return saveform(djp, force_redirect = self.force_redirect)
    
    def success_message(self, instance, mch):
        return ''
    
    def has_permission(self, *args, **kwargs):
        return True


class UserView(views.ViewView):
    
    def title(self, djp):
        return djp.instance.username
            
            
class UserDataView(UserView):
    
    def render(self, djp):
        return ''
    