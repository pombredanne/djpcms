import os
from copy import copy

from . import http
from .site import get_settings, Site


__all__ = ['SiteLoader']


class SiteLoader(object):
    '''An class for loading and configuring djpcms sites. Users can
subclass this class and override the :meth:`load` method.
 
.. attribute:: name

    The configuration name, useful when different types of configuration are
    needed (WEB, RPC, ...)
     
    default: ``"DJPCMS"``

.. attribute:: sites

    instance of :class:`Site` lazily created when an instance of this
    class is called.
'''
    ENVIRON_NAME = None
    settings = None
    
    def __init__(self, name = None, **params):
        self.sites = None
        self._wsgi_middleware = []
        self._response_middleware = []
        self.name = name or 'DJPCMS'
        self.setup(**params)
        
    def setup(self, **params):
        self.params = params
        
    def __getstate__(self):
        d = self.__dict__.copy()
        d['local'] = {}
        d['sites'] = None
        d['_wsgi_middleware'] = []
        d['_response_middleware'] = []
        return d
        
    def __call__(self):
        return self.build_sites()
    
    def add_wsgi_middleware(self, m):
        '''Add a wsgi callable middleware or a list of middlewares'''
        if isinstance(m,(list,tuple)):
            self._wsgi_middleware.extend(m)
        else:
            self._wsgi_middleware.append(m)
        
    def add_response_middleware(self, m):
        '''Add a callable response middleware or a list of middleware'''
        if isinstance(m,(list,tuple)):
            self._response_middleware.extend(m)
        else:
            self._response_middleware.append(m)
    
    def build_sites(self):
        if self.sites is None:
            if self.ENVIRON_NAME:
                os.environ[self.ENVIRON_NAME] = self.name
            name = '_load_{0}'.format(self.name.lower())
            self.sites = getattr(self,name,self.load)()
            if self.sites is not None:
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
        '''Return a list of response middleware.'''
        sites = self.build_sites()
        return self._response_middleware or []
    
    def load(self):
        '''create the :class:`Site` for your web.

:rtype: an instance of :class:`Site`.
'''
        settings = get_settings(settings = self.settings)
        return Site(settings)
        
    def finish(self):
        '''Callback once the sites are loaded.'''
        pass
    
    def on_server_ready(self, server):
        '''Optional callback by a server just before start serving.'''
        pass

    def wsgi(self):
        '''Return the WSGI handeler for your application.'''
        return http.WSGIhandler(self.wsgi_middleware(),
                                self.response_middleware())
