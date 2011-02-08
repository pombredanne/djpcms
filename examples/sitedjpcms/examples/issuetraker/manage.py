'''
Script for running a stand-alone IssueTracker application

Requires python-stdnet

To run the server simply::

    python manage.py serve
    
To create style sheet::

    python manage.py style

'''
from vws import virtual
virtual(('djpcms','djpcms'),
        ('stdnet','python-stdnet'))

import djpcms
from djpcms.apps.management import execute


def appurls():
    from djpcms import sites
    from djpcms.apps.included import user, static, contentedit
    from stdnet.contrib.sessions.models import User
    from djpcms.models import Page
    from .application import IssueTraker, Issue
    
    return (
            static.Static(sites.settings.MEDIA_URL, show_indexes=True),
            user.UserApplication('/accounts/', User),
            contentedit.PageApplication('/edit-content/', Page),
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
    return djpcms.sites
    
    
if __name__ == '__main__':
    build()
    execute()


