'''
Script for running a stand-alone Playground Web application.
To run the server simply::

    python manage.py serve
    
To create the style sheet::

    python manage.py style

'''
import djpcms
from djpcms.apps import static
from djpcms.html.layout import page, row, column, container
from djpcms.apps.nav import topbar

class Loader(djpcms.WebSite):
    
    def load(self):
        settings = djpcms.get_settings(
                __file__,
                APPLICATION_URLS = self.urls,
                INSTALLED_APPS = ('djpcms',
                                  'djpcms.style.plugins',
                                  'djpcms.apps.nav',
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
        # Page layout
        page(
             topbar(brand = 'Playground'),
             container(
             row(column(1,1,renderer = self.page_header_layout),
                 id = 'page-header',
                 role = 'header'),
             row(column(1, 3, key = 'sitenav'),
                 column(2, 3, key = 'inner')),
             row(role =  'footer',
                 renderer = self.page_footer_layout)),
             role = 'page',
             id = 'body-container').register('default')
            
    def page_header_layout(self, request, widget, context):
        return '<h2>'+context['title']+'</h2>'
    
    def page_footer_layout(self, request, widget, context):
        return '<p>djpcms example</p>'
            
    
if __name__ == '__main__':
    djpcms.execute(Loader())