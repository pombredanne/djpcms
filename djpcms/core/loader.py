import os
from copy import copy

from . import http
from .site import get_settings, Site


__all__ = ['SiteLoader']


class SiteLoader(object):
    '''An utility class for loading and configuring djpcms sites.
 
 .. attribute:: name
 
     The configuration name, useful when different types of configuration are
     needed (WEB, RPC, ...)
'''
    ENVIRON_NAME = None
    settings = None
    
    def __init__(self, name = None, **params):
        self.sites = None
        self._wsgi_middleware = None
        self._response_middleware = None
        self.name = name or 'DJPCMS'
        self.setup(**params)
        
    def setup(self, **params):
        self.params = params
        
    def __getstate__(self):
        d = self.__dict__.copy()
        d['sites'] = None
        d['_wsgi_middleware'] = None
        d['_response_middleware'] = None
        return d
        
    def __call__(self):
        return self.build_sites()
    
    def build_sites(self):
        if self.sites is None:
            if self.ENVIRON_NAME:
                os.environ[self.ENVIRON_NAME] = self.name
            name = '_load_{0}'.format(self.name.lower())
            self.sites = getattr(self,name,self.load)()
            if self.sites:
                self.sites.load()
                self.finish()
        return self.sites
    
    def wsgi_middleware(self):
        '''Return a list of WSGI middleware for serving wsgi requests.'''
        sites = self.build_sites()
        m = self._wsgi_middleware or []
        m = copy(m)
        m.append(http.WSGI(sites))
        return m
    
    def response_middleware(self):
        sites = self.build_sites()
        return self._response_middleware or []
    
    def load(self):
        '''Default loading'''
        settings = get_settings(settings = self.settings)
        return Site(settings)
        
    def finish(self):
        '''Callback once the sites are loaded.'''
        pass
    
    def on_server_ready(self, server):
        '''Optional callback by a server just before start serving.'''
        pass

    def wsgi(self):
        return http.WSGIhandler(self.wsgi_middleware(),
                                self.response_middleware())
