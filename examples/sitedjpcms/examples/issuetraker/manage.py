'''
Script for running a stand-alone IssueTracker application

Requires python-stdnet

To run the server simply::

    python manage.py serve
    
To create style sheet::

    python manage.py style

'''
import djpcms
from djpcms.apps.management import execute


def appurls():
    from djpcms import sites
    from djpcms.apps.included import user, static
    from stdnet.contrib.sessions.models import User
    from .application import IssueTraker, Issue
    
    return (
            static.Static(sites.settings.MEDIA_URL, show_indexes=True),
            user.UserApplication('/accounts/', User),
            IssueTraker('/',Issue),
            )


def build():
    djpcms.MakeSite(__file__,
                APPLICATION_URL_MODULE = 'issuetraker.manage',
                USER_MODEL = 'issuetraker.models.User',
                CMS_ORM = 'stdnet',
                TEMPLATE_ENGINE = 'django',
                INSTALLED_APPS = ('djpcms',
                                  'issuetraker',
                                  'stdnet.contrib.sessions',
                                  'djpcms.contrib.medplate'),
                MIDDLEWARE_CLASSES = ('djpcms.middleware.CreateRootPageAndUser',
                                      'stdnet.contrib.sessions.middleware.SessionMiddleware',),
                DEBUG = True
                )
    
    
if __name__ == '__main__':
    build()
    execute()


