from djpcms import test, sites
from djpcms.apps.included.user import UserApplication



# A web site with user pages
def appurls1():
    from .models import User, Portfolio
    apps = (Application('/portfolio/', Portfolio,
                        parent = 'userhome'),)
    return (CustomUserApp('/',
                          User, apps = apps),
            )


@test.skipUnless(sites.tests.CMS_ORM,"Testing without ORM")
class TestSiteUser1(test.TestCase, test.UserMixin):
    appurls = 'regression.userapp.tests.appurls1'
    NUMVIEWS = USER_NUMVIEWS
    
    