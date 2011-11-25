from djpcms.utils import test
from djpcms.apps.user import UserApplication


@test.skipUnless(test.djpapps,"Requires djpapps installed")
class UserApp(test.TestCase):
    
    def appurls1():
        from sessions.models import User
        from .models import User, Portfolio
        apps = (Application('/portfolio/', Portfolio,
                            parent = 'userhome'),)
        return (CustomUserApp('/',
                              User, apps = apps),
                ) 
    
    
    