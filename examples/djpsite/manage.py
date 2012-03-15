#!/usr/bin/env python
'''
Script for running djpcms web site. It requires the following libraries:

* style_
* https://github.com/lsbardel/stdcms
* https://github.com/lsbardel/social

To run the server simply::

    python manage.py serve
    
To create the style sheet::

    python manage.py style

'''
import djpcms
from djpcms.apps import static
from djpcms.html.layout import page, row, column, container
from djpcms.apps.nav import topbar
    
    
class WebSite(djpcms.WebSite):
    
    def load(self):
        settings = djpcms.get_settings(
                __file__,
                APPLICATION_URLS = self.urls,
                INSTALLED_APPS = ('djpcms',
                                  'style',
                                  'stdcms',
                                  'stdcms.cms',
                                  'stdcms.monitor',
                                  'stdcms.sessions'),
                ENABLE_BREADCRUMBS = 1,
                FAVICON_MODULE = 'djpcms',
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
                #Geonames('/geo/'),
                #PlayGround('/')
                )
    
    def page_layout(self):
        # Page layout
        page(container('header', topbar(brand = 'Playground')),
             container('content'),
             grid(row(column(1)))).register('default')
            
    def page_header_layout(self, request, widget, context):
        return '<h2>'+context['title']+'</h2>'
    
    def page_footer_layout(self, request, widget, context):
        return '<p>djpcms example</p>'
    

if __name__ == '__main__':
    djpcms.execute(WebSite())
