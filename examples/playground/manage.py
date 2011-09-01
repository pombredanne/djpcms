'''
Script for running a stand-alone Playground Web application.
To run the server simply::

    python manage.py serve
    
To create the style sheet::

    python manage.py style

'''
import djpcms


class Loader(object):
    loaded = False
    
    def __call__(self):
        if not self.loaded:
            self.loaded = True
            djpcms.MakeSite(__file__,
                APPLICATION_URLS = self.urls,
                INSTALLED_APPS = ('djpcms',
                                  'medplate',
                                  'playground'),
                ENABLE_BREADCRUMBS = 1,
                # the favicon to use is in the djpcms module
                FAVICON_MODULE = 'djpcms',
                # the profiling key to profile
                PROFILING_KEY = 'prof',
                DEBUG = True
                )
        return djpcms.sites
    
    def urls(self):
        from djpcms.apps.included import static
        from playground.application import PlayGround, Geonames
        
        # we serve static files too in this case
        return (
                static.FavIcon(),
                static.Static(djpcms.sites.settings.MEDIA_URL,
                              show_indexes=True),
                Geonames('/geo/'),
                PlayGround('/')
                )
    
    
if __name__ == '__main__':
    djpcms.execute(Loader())