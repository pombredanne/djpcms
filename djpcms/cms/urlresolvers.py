import re
from inspect import isclass
from copy import copy
from threading import Lock
from collections import namedtuple

from djpcms.utils.text import UnicodeMixin
from djpcms.utils.httpurl import iteritems, itervalues
from djpcms.utils.structures import OrderedDict

from .exceptions import *
from .routing import Route
from .tree import NRT
from .views import RouteMixin, url_match


__all__ = ['ResolverMixin']
        

class resolver_manager(object):
    '''A Context manager for injecting the trypath attribute to the Http404
 exception. If the the resolver raised a Http4040 exception and the path does
 not end with a trailing slash, we check if the path with the trailing slash is
 correct. If so, with put ist value into the *trypath* attribute of the
 exception.'''
    def __init__(self, resolver, path):
        self.resolver = resolver
        self.path = path
        
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        path = self.path
        if isinstance(value, Http404):
            value.url = None
            if self.resolver.is_root and path and not path.endswith('/'):
                path = path+'/'
                try:
                    v,u = self.resolver.resolve(path)
                except:
                    pass
                else:
                    value.url = '/'+path
    
    
class ResolverMixin(RouteMixin):
    '''A :class:`RouteMixin` for classes with several sub-routes. An instance
 of this class has always :attr:`is_leaf` equal to ``False``, it is guaranteed
 to be a route directory.
    
.. attribute:: routes

    dictionary of :class:`RouteMixin` instances representing the sub-routes
    for this instance.
    
'''
    def __init__(self, route, routes=None):
        self.routes = [] if not routes else list(routes)
        if not isinstance(route, Route):
            route = Route(route, append_slash=True)
        if route.is_leaf:
            raise ValueError('A resolver cannot have a leaf route {0}'\
                             .format(route))
        super(ResolverMixin, self).__init__(route)
    
    def __unicode__(self):
        return '{0} - {1}'.format(self.path,list(self))
    
    def __len__(self):
        return len(self.routes)
    
    def count(self):
        return len(self.routes)
    
    def __iter__(self):
        return iter(self.routes)
    
    def __getitem__(self, index):
        return self.routes[index]
    def __setitem(self, index, val):
        raise TypeError('Site object does not support item assignment')
    
    def load(self):
        '''Load urls and set-up sites'''
        if not self.isbound:
            self.local['urls'] = self._load()
            self.on_bound()
            if self.is_root and self:
                self.local['tree'] = NRT(self.all_views(),self)
        
    def _isbound(self):
        return 'urls' in self.local
    
    def urls(self):
        self.load()
        return self.local['urls']
    
    def _load(self):
        if not self.routes:
            raise ImproperlyConfigured('No sites registered with {0}.'\
                                       .format(self))
        for route in self:
            if route.isbound:
                raise ImproperlyConfigured('Route {0} already bound.'\
                                           .format(route))
            route.parent = self
            route.load()
        return tuple(self)
    
    def make_url(self, route, handler, name=None):
        return (route, handler, name)
    
    def all_views(self):
        '''generator of all application views in self.'''
        for child in self:
            if isinstance(child,ResolverMixin):
                for route in child.all_views():
                    yield route
            else:
                yield child
    
    def match(self, path):
        match = self.rel_route.match(path)
        if match:
            remaining_path = match.pop('__remaining__','')
            try:
                return self.resolve(remaining_path)
            except Http404:
                pass
            
    def resolve(self, path, urlargs=None):
        '''Resolve a *path* recursively.'''
        try:
            with resolver_manager(self, path) as rm:
                urlargs = urlargs if urlargs is not None else {}
                best_match = url_match(self, urlargs, path)
                for handler in self.urls():
                    match = handler.rel_route.match(path)
                    if match is None:
                        continue
                    remaining_path = match.pop('__remaining__','')
                    urlargs.update(match)
                    if isinstance(handler, ResolverMixin):
                        try:
                            return handler.resolve(remaining_path, urlargs)
                        except Http404 as e:
                            remaining_path = e.handler.remaining
                            if len(remaining_path) <= len(best_match.remaining):
                                best_match = e.handler
                    elif not remaining_path:
                        return handler, urlargs
                raise Http404(path, handler=best_match)
        except Http404 as e:
            if e.url:
                raise HttpRedirect(e.url)
            else:
                raise
            
    def pageview(self, path):
        Page = self.root.Page
        if Page:
            from djpcms.views import pageview
            try:
                return pageview(Page.get(url = path.path),self)
            except Page.DoesNotExist:
                pass
    
    def for_model(self, model):
        '''Obtain a :class:`djpcms.views.appsite.ModelApplication` for *model*.
If the application is not available, it returns ``None``. It never fails.'''
        return None
    
    def _make_parent(self, parent):
        parent = super(ResolverMixin, self)._make_parent(parent)
        #loop over routes and set the new parent
        for route in self:
            route.parent = self
        return parent

    def on_bound(self):
        '''Callback when the resolver is bound to the :attr:`parent` resolver.
 By default it does nothing, but it can be used to configure things once the
 resolver map is ready.'''
        pass
    
    def applications(self):
        '''generator of registered applications'''
        raise NotImplementedError
