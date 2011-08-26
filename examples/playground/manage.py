'''
Script for running a stand-alone Playground Web application.
To run the server simply::

    python manage.py serve
    
To create style sheet::

    python manage.py style -s smooth

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
                DJPCMS_PLUGINS = ('djpcms.plugins.*',
                                  'djpcms.apps.included.contentedit.plugins'),
                INSTALLED_APPS = ('djpcms',
                                  'medplate',
                                  # issuetracker must be last for styling
                                  'playground'),
                PROFILING_KEY = 'prof'
                )
        return djpcms.sites
    
    def urls(self):
        from djpcms.apps.included import static
        from playground.application import PlayGround
        
        return (
                static.Static(djpcms.sites.settings.MEDIA_URL,
                              show_indexes=True),
                PlayGround('/'),
                )
    
    
if __name__ == '__main__':
    execute(Loader())