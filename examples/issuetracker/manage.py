'''
Script for running a stand-alone IssueTracker application

Requires python-stdnet https://github.com/lsbardel/python-stdnet

To install it just type::

    pip install python-stdnet
    or
    easy_install python-stdnet
    

To run the server simply::

    python manage.py serve
    
To create style sheet::

    python manage.py style -t media/site/site.css -s smooth

'''
import djpcms
from djpcms.apps.management import execute


class Loader(object):
    loaded = False
    
    def __call__(self):
        if not self.loaded:
            self.loaded = True
            djpcms.MakeSite(__file__,
                            APPLICATION_URLS = self.urls,
                            CMS_ORM = 'stdnet',
                            DEFAULT_INNER_TEMPLATE = 'djpcms/inner/cols3_25_50_25.html',
                            DJPCMS_PLUGINS = ('djpcms.plugins.*',
                                              'djpcms.apps.included.contentedit.plugins'),
                            INSTALLED_APPS = ('djpcms',
                                              'djpcms.contrib.monitor',
                                              'djpcms.contrib.sessions',
                                              'medplate',
                                              'issuetracker'),   # issuetracker must be last for styling
                            MIDDLEWARE_CLASSES = ('djpcms.contrib.sessions.middleware.SessionMiddleware',),
                            DEBUG = True
                            )
        return djpcms.sites
    
    def urls(self):
        from djpcms.apps.included import user, static
        from djpcms.contrib.sessions.models import User
        from issuetracker.application import IssueTraker, Issue
        
        return (
                static.Static(djpcms.sites.settings.MEDIA_URL, show_indexes=True),
                user.UserApplication('/accounts/', User),
                IssueTraker('/',Issue),
                )
    
    
if __name__ == '__main__':
    execute(Loader())


