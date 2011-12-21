import os
from copy import copy

from . import http
from .site import get_settings, Site
from .exceptions import ImproperlyConfigured


__all__ = ['SiteLoader']


class SiteLoader(object):
    '''A class for callable instances for loading and configuring sites.
Users can subclass this class and override the :meth:`load` method or
the ``load_{{ name }}`` where ``name`` is the value of the
:attr:`name` attribute.
Instances are pickable so that they can be used to create site applications
in a multiprocessing framework.
 
.. attribute:: name

    The configuration name, useful when different types of configuration are
    needed (WEB, RPC, ...)
     
    default: ``"DJPCMS"``

.. attribute:: site

    instance of :class:`Site` lazily created when an instance of this
    class is called.
        
.. attribute:: wsgi_middleware
    
    A list of WSGI_ middleware callables created during the loading of the
    application.
    
.. attribute:: response_middleware

    A list of response middleware callables created during the loading of the
    application.

'''
    ENVIRON_NAME = None
    settings = None
    
    def __init__(self, name = None, **params):
        self.local = {}
        self.name = name or 'DJPCMS'
        self.setup(**params)
        
    def setup(self, **params):
        self.params = params
        
    def __getstate__(self):
        d = self.__dict__.copy()
        d['local'] = {}
        return d
    
    @property
    def site(self):
        return self.local.get('site')
    
    @property
    def _wsgi_middleware(self):
        if '_wsgi_middleware' not in self.local:
            self.local['_wsgi_middleware'] = []
        return self.local['_wsgi_middleware']
    
    @property
    def _response_middleware(self):
        if '_response_middleware' not in self.local:
            self.local['_response_middleware'] = []
        return self.local['_response_middleware']
    
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
    
    def __call__(self):
        if self.site is None:
            if self.ENVIRON_NAME:
                os.environ[self.ENVIRON_NAME] = self.name
            name = 'load_{0}'.format(self.name.lower())
            loader = getattr(self,name,self.load)
            self.local['site'] = loader()
            if self.site is not None:
                try:
                    self.site.load()
                except ImproperlyConfigured:
                    if getattr(loader,'web_site',True):
                        raise
                self.finish()
        return self.site
    
    def wsgi_middleware(self):
        '''Return a list of WSGI middleware for serving wsgi requests.'''
        site = self()
        m = self._wsgi_middleware or []
        m = copy(m)
        m.append(http.WSGI(site))
        return m
    
    def response_middleware(self):
        '''Return a list of response middleware.'''
        site = self()
        return self._response_middleware or []
    
    def load(self):
        '''create the :class:`Site` for your web.

:rtype: an instance of :class:`Site`.
'''
        settings = get_settings(settings = self.settings)
        return Site(settings)
        
    def finish(self):
        '''Callback once the site are loaded.'''
        pass
    
    def on_server_ready(self, server):
        '''Optional callback by a server just before start serving.'''
        pass

    def wsgi(self):
        '''Return the WSGI handeler for your application.'''
        return http.WSGIhandler(self.wsgi_middleware(),
                                self.response_middleware())
