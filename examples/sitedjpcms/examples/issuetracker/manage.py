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
from vws import virtual
virtual(('djpcms','djpcms'),
        ('stdnet','python-stdnet'))

import djpcms
from djpcms.apps.management import execute


def appurls():
    from djpcms import sites
    from djpcms.apps.included import user, static, contentedit
    from stdnet.contrib.sessions.models import User
    from djpcms.models import Page, BlockContent
    from .application import IssueTraker, Issue
    
    return (
            static.Static(sites.settings.MEDIA_URL, show_indexes=True),
            user.UserApplication('/accounts/', User),
            contentedit.ContentSite('/edit/block/', BlockContent),
            contentedit.PageApplication('/edit/', Page),
            IssueTraker('/',Issue),
            )


def build():
    djpcms.MakeSite(__file__,
                    APPLICATION_URL_MODULE = 'issuetracker.manage',
                    CMS_ORM = 'stdnet',
                    DEFAULT_INNER_TEMPLATE = 'djpcms/inner/cols3_25_50_25.html',
                    DJPCMS_PLUGINS = ('djpcms.plugins.*',
                                      'djpcms.apps.included.contentedit.plugins'),
                    INSTALLED_APPS = ('djpcms',
                                      'stdnet.contrib.monitor',
                                      'stdnet.contrib.sessions',
                                      'medplate',
                                      'issuetracker'),   # issuetracker must be last for styling
                    MIDDLEWARE_CLASSES = ('djpcms.middleware.CreateRootPageAndUser',
                                          'stdnet.contrib.sessions.middleware.SessionMiddleware',),
                    DEBUG = True
                    )
    return djpcms.sites
    
    
if __name__ == '__main__':
    build()
    execute()


