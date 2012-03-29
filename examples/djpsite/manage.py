#!/usr/bin/env python
'''
Script for running djpcms web site. It requires the following libraries:

* style_
* https://github.com/lsbardel/stdcms
* https://github.com/lsbardel/social

You need to create a settings.py file and assign the `RESERVED SETTINGS`
parameters in `conf.py` module. The file should look like::

    from .conf import *
    SECRET_KEY = ...
    ...

To run the server simply::

    python manage.py serve
    
To create the style sheet::

    python manage.py style

'''
import sys

import djpcms
from djpcms import views
from djpcms.apps import admin, static, user
from djpcms import html
from djpcms.html.layout import page, container, grid
from djpcms.plugins.navigation import topbar

from stdcms.sessions.handler import PermissionHandler
    
    
class MainApplication(views.Application):
    home = views.View('/')
    favicon = static.FavIconView()
    
    
class WebSite(djpcms.WebSite):
    '''djpcms website'''
    def load(self):
        config = self.params.get('config', 'djpsite.conf')
        settings = djpcms.get_settings(
                __file__,
                config,
                APPLICATION_URLS = self.urls,
                DEBUG = True
            )
        permissions = PermissionHandler(settings)
        backend = permissions.auth_backends[0]
        # AUTHENTICATION MIDDLEWARE
        self.add_wsgi_middleware(backend.request_middleware())        
        # AUTHENTICATION RESPONSE MIDDLEWARE
        self.add_response_middleware(backend.process_response)
        
        # The root site
        site = djpcms.Site(settings, permissions=permissions)
        # admin site
        settings = djpcms.get_settings(
            __file__,
            config,
            APPLICATION_URLS  = admin.make_admin_urls())
        permissions = PermissionHandler(settings,
                                        auth_backends=[backend],
                                        requires_login=True)
        site.addsite(settings, route='/admin/', permissions=permissions)
        self.page_layouts(site)
        return site
    
    def urls(self, site):
        #from playground.application import PlayGround, Geonames
        # we serve static files too in this case
        return (
                static.Static(site.settings.MEDIA_URL,
                              show_indexes=True),
                user.UserApplication('/accounts/', site.User),
                MainApplication('/')
                )
    
    def page_layouts(self, site):
        # Page template
        page_template = page(
            container('edit'),
            container('topbar',
                      grid('grid 100'),
                      cn = 'topbar-fixed',
                      role = 'topbar'),
            container('header', grid('grid 100'), role = 'header'),
            container('content', role = 'content'),
            container('footer', grid('grid 33-33-33'), role = 'footer'))
        site.register_page_layout('default', page_template)
        page_template.renderers['topbar'] = self.render_topbar
        page_template.renderers['header'] = self.render_header
        page_template.renderers['footer'] = self.render_footer
            
    def render_topbar(self, request, block_number, blocks):
        '''Render the topbar container'''
        return ''
        if block_number == 0:
            return topbar(request)
    
    def render_header(self, request, block_number, blocks):
        if block_number == 0:
            return '<h2>Dynamic Content management system</h2>'
    
    def render_footer(self, request, block_number, blocks):
        if block_number == 0:
            return '<p>djpcms</p>'
        elif block_number == 2:
            return '<p>Powered by <a href="http://www.python.org">Python'\
                   ' {0}.{1}.{2}</a></p>'.format(*sys.version_info[:3])
        else:
            return html.NON_BREACKING_SPACE
        
    

if __name__ == '__main__':
    djpcms.execute(WebSite(config = 'djpsite.settings'))
