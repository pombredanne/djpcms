from djpcms import sites, views
from djpcms.forms.utils import saveform

from .orm import logout

__all__ = ['LogoutView','LoginView','UserView','UserDataView']



class LogoutView(views.ModelView):
    '''
    Logs out a user, if there is an authenticated user :)
    '''
    _methods = ('get',)
    
    def __init__(self, regex = 'logout', parent = None):
        super(LogoutView,self).__init__(regex = regex,
                                        parent = parent,
                                        insitemap = False)
        
    def preprocess(self, djp):
        request = djp.request
        params  = dict(request.GET.items())
        url     = params.get('next',None) or '/'
        user    = request.user
        if user.is_authenticated():
            logout(sites.User, request)
        return djp.http.HttpResponseRedirect(url)



class LoginView(views.ModelView):
    '''A Battery included Login view. You need to
    create a login.html file in your site template directory.
    '''
    default_title = 'Sign in'
    template_name = 'login.html'
    def __init__(self,
                 regex = 'login',
                 isplugin = True,
                 **kwargs):
        super(LoginView,self).__init__(regex = regex,
                                       isplugin = isplugin,
                                       force_redirect = True,
                                       **kwargs)
        
    def preprocess(self, djp):
        if djp.request.user.is_authenticated():
            return djp.http.HttpResponseRedirect('/')
        
    def render(self, djp):
        if djp.request.user.is_authenticated():
            return ''
        else:
            return self.get_form(djp).render(djp)
    
    def default_post(self, djp):
        return saveform(djp, force_redirect = self.force_redirect)
    
    def success_message(self, instance, mch):
        return ''


class UserView(views.ViewView):
    
    def title(self, djp):
        return djp.instance.username
            
            
class UserDataView(UserView):
    
    def render(self, djp):
        return ''
    