'''
Script for running a stand-alone Playground Web application.
To run the server simply::

    python manage.py serve
    
To create the style sheet::

    python manage.py style

'''
import djpcms
from djpcms.apps import static
from djpcms import html

class Loader(djpcms.SiteLoader):
    
    def load(self):
        settings = djpcms.get_settings(
                __file__,
                APPLICATION_URLS = self.urls,
                INSTALLED_APPS = ('djpcms',
                                  #'medplate',
                                  'playground'),
                ENABLE_BREADCRUMBS = 1,
                # the favicon to use is in the djpcms module
                FAVICON_MODULE = 'djpcms',
                # the profiling key to profile
                PROFILING_KEY = 'prof',
                DEFAULT_STYLE_SHEET = {'all':[
'http://yui.yahooapis.com/2.9.0/build/reset-fonts-grids/reset-fonts-grids.css',
"playground/smooth.css"]},
                DEBUG = True
            )
        self.page_layout()
        return djpcms.Site(settings)
    
    def urls(self, site):
        from playground.application import PlayGround, Geonames
        # we serve static files too in this case
        return (
                static.Static(site.settings.MEDIA_URL,
                              show_indexes=True),
                Geonames('/geo/'),
                PlayGround('/')
                )
    
    def page_layout(self):
        html.page_layout(
            html.page_row(key = 'title',
                          id = 'page-header',
                          role = 'header',
                          renderer = self.render_header),
            html.page_row(html.grid(1,3, key = 'sitenav'),
                          html.grid(2,3, key = 'inner')),
            html.page_row(role =  'footer'),
            role = 'page',
            id = 'body-container').register('default')
            
    def render_header(self):
    
if __name__ == '__main__':
    djpcms.execute(Loader())