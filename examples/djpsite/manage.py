#!/usr/bin/env python
'''
Script for running djpcms web site. It requires the following libraries:

* https://github.com/lsbardel/python-stdnet
* https://github.com/lsbardel/stdcms
* https://github.com/lsbardel/social

You need to create a settings.py file in the same directory as this script
and assign the `RESERVED SETTINGS` parameters in the `conf.py` module.
The file should look like::

    from .conf import *
    SECRET_KEY = ...
    ...

To run the server simply::

    python manage.py serve
    
To create the style sheet::

    python manage.py style

'''
import sys

from djpcms import cms, views, html
from djpcms.apps import admin, static, user
from djpcms.html import Widget
from djpcms.html.layout import page, container, grid
from djpcms.apps.nav import topbar

from stdcms.sessions import User
from stdcms.sessions.handler import PermissionHandler

from social.applications import SocialUserApplication
    
    
class UserApplication(SocialUserApplication):
    login = user.LoginView()
    
    
class MainApplication(views.Application):
    home = views.View('/')
    favicon = static.FavIconView()
    
    
class WebSite(cms.WebSite):
    settings_file = 'djpsite.settings'
    def load(self):
        settings = cms.get_settings(
                __file__,
                self.settings_file,
                APPLICATION_URLS = self.urls,
                DEBUG = True
            )
        permissions = PermissionHandler(settings)
        backend = permissions.auth_backends[0]
        # AUTHENTICATION MIDDLEWARE
        self.add_wsgi_middleware(permissions.request_middleware())
        self.add_response_middleware(permissions.response_middleware())
        
        # The root site
        site = cms.Site(settings, permissions=permissions)
        # admin site
        settings = cms.get_settings(
            __file__,
            self.settings_file,
            APPLICATION_URLS  = admin.make_admin_urls())
        permissions = PermissionHandler(settings,
                                        auth_backends=permissions.auth_backends,
                                        requires_login=True)
        site.addsite(settings, route='/admin/', permissions=permissions)
        self.page_layouts(site)
        return site
    
    def urls(self, site):
        from djpsite.apps import design
        return (
                #Serve static files during development
                static.Static(site.settings.MEDIA_URL),
                design.DesignApplication('/design', design.Theme),
                UserApplication('/accounts/', User),
                MainApplication('/')
                )
    
    def page_layouts(self, site):
        # Page template
        page_template = page(
            container('topbar', grid('grid 100'), cn='topbar-fixed',
                      renderer=self.render_topbar),
            container('header', grid('grid 100'),
                      renderer=self.render_header),
            container('content'),
            container('footer', grid('grid 33-33-33'),
                      renderer=self.render_footer))
        tiny_template = page(container('header', grid('grid 100')),
                             container('content'),
                             container('footer', grid('grid 100')))
        site.register_page_layout('default', page_template)
        site.register_page_layout('tiny', tiny_template)
    
    def render_topbar(self, request, namespace, column, blocks):
        '''Render the topbar container'''
        if column == 0:
            return topbar(request).render(request)
    
    def render_header(self, request, namespace, column, blocks):
        if column == 0:
            return '<h2>Dynamic content management system for Python</h2>'
    
    def render_footer(self, request, namespace, column, blocks):
        if column == 0:
            link = Widget('a','BSD license',
                    href='http://www.opensource.org/licenses/bsd-license.php')\
                    .addAttr('target','_blank')
            return Widget('p', ('djpcms code is licensed under ',link,'.'))
        elif column == 2:
            return '<p>Powered by <a href="http://www.python.org">Python'\
                   ' {0}.{1}.{2}</a></p>'.format(*sys.version_info[:3])
        else:
            return html.NON_BREACKING_SPACE
        
    

if __name__ == '__main__':
    cms.execute(WebSite())
