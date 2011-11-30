import re
from inspect import isclass
from copy import copy, deepcopy
from threading import Lock

from py2py3 import is_bytes_or_string, iteritems, itervalues

from djpcms import UnicodeMixin
from djpcms.utils import force_str
from djpcms.utils.structures import OrderedDict
from djpcms.utils.importer import import_modules

from .exceptions import *
from .routing import Route
from . import http


__all__ = ['RouteMixin','ResolverMixin']


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
        if isinstance(value,Http404) and not self.path.endswith('/'):
            try:
                v,u,k = self.resolver.resolve(self.path+'/')
            except:
                pass
            else:
                value.trypath = self.path+'/'
                

class RouteMixin(UnicodeMixin):
    '''Class for routing trees, This class is the base class for all
routing and handler classes in djpcms including, but not only, :class:`Site`,
:class:`djpcms.views.Application` and :class:`djpcms.views.View`.
    
:parameter route: A :class:`Route` instance or a route string, it is used
    to set the :attr:`rel_route` attribute.
    
:parameter parent: It sets the :attr:`parent` attribute.

    Default: ``None``.
    

--


**Attributes**

    
.. attribute:: parent

    The :class:`RouteMixin` immediately before this route. Used to build
    :attr:`route` from the :attr:`rel_route` attribute. When setting this
    attribute, the :attr:`route` attribute will get updated.
    
.. attribute:: route

    The :class:`Route` for this instance
    
.. attribute:: rel_route

    The relative :class:`Route` with respect :attr:`parent` for this instance.
    
.. attribute:: path

    proxy to the :attr:`Route.path` attribute of :attr:`route`.
    It is the absolute path for this instance.
    
.. attribute:: isbound

    ``True`` when the route is bound to a :class:`ResolverMixin` instance.
    
.. attribute:: root

    The root :class:`RouteMixin` instance for of this route. If this instance
    has :attr:`parent` set to ``None``, the :attr:`root` is equal to ``self``.
    
.. attribute:: site

    The closes :class:`Site` instance for of this route.
    
.. attribute:: settings

    web site settings dictionary, available when :attr:`isbound` is ``True``.
'''
    def __init__(self, route, parent = None):
        self.lock = Lock()
        if not isinstance(route,Route):
            route = Route(route)
        self.__rel_route = route
        self.__route = route
        self.__parent = None
        self.parent = parent
        self.internals = {}
        
    def __unicode__(self):
        return self.route.rule
        
    def _get_parent(self):
        return self.__parent
    def _set_parent(self, parent):
        if parent is not self.__parent:
            self.__parent = self.make_parent(parent)
    parent = property(_get_parent,_set_parent)
    
    def __get_rel_route(self):
        return self.__rel_route
    def __set_rel_route(self, r):
        if self.__route == self.__rel_route:
            self.__rel_route = r
            self.__route = r
        else:
            br = self.__route - self.rel_route
            self.__rel_route = r
            self.__route = br + r
    rel_route = property(__get_rel_route,__set_rel_route)
    
    @property
    def site(self):
        return self._site()
    
    @property
    def route(self):
        return self.__route
    
    @property
    def path(self):
        return self.route.path
    
    @property
    def root(self):
        if self.parent is not None:
            return self.parent.root
        else:
            return self
    
    @property
    def isbound(self):
        return self._isbound()
    
    def internal_data(self, name):
        v = self.internals.get(name)
        if v is None and self.parent:
            return self.parent.internal_data(name)
        else:
            return v
    
    def render_response(self, response, callback = None):
        return self.response_handler(self, response, callback)
    
    def unwind_query(self, query, callback = None):
        return self.response_handler(self, query, callback)
    
    @property
    def settings(self):
        return self.internal_data('settings')
    
    @property
    def tree(self):
        return self.internal_data('tree')
    
    @property
    def search_engine(self):
        return self.internal_data('search_engine')
    
    @property
    def permissions(self):
        return self.internal_data('permissions')
    
    @property
    def robots(self):
        return self.internal_data('robots')
    
    @property
    def response_handler(self):
        return self.internal_data('response_handler')
    
    @property
    def template(self):
        return self.internal_data('template')
    
    @property
    def User(self):
        return self.internal_data('User')
    
    @property
    def Page(self):
        return self.internal_data('Page')
    
    @property
    def BlockContent(self):
        return self.internal_data('BlockContent')
    
    @property
    def storage(self):
        return self.internal_data('storage')
    
    def make_parent(self, parent):
        if parent is not None:
            if not isinstance(parent, RouteMixin):
                raise ValueError('parent must be an instance of RouteMixin.\
 Got "{0}"'.format(parent))
            self.__route = parent.route + self.__rel_route
        else:
            self.__route = self.__rel_route
        return parent
    
    def _site(self):
        raise NotImplementedError
    
    def _isbound(self):
        raise NotImplementedError
    
    
class ResolverMixin(RouteMixin):
    '''A :class:`RouteMixin` for classes with several sub-routes. An instance
 of this class has always :attr:`is_leaf` equal to ``False``, it is guaranteed
 to be a route directory.
    
.. attribute:: routes

    dictionary of :class:`RouteMixin` instances representing the sub-routes
    for this instance.
    
'''
    def __init__(self, route, parent = None):
        self.routes = []
        if not isinstance(route,Route):
            route = Route(route, append_slash = True)
        if route.is_leaf:
            raise ValueError('A resolver cannot have a leaf route {0}'\
                             .format(route))
        super(ResolverMixin,self).__init__(route,parent)
        
    def __deepcopy__(self,memo):
        obj = copy(self)
        obj.routes = deepcopy(self.routes)
        return obj
    
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
        if not hasattr(self,'_urls'):
            self._urls = self._load()
            self.on_bound()
        
    def _isbound(self):
        return hasattr(self,'_urls')
    
    def urls(self):
        self.load()
        return self._urls
    
    def _load(self):
        if not self.routes:
            raise ImproperlyConfigured('No sites registered.')
        for site in self:
            site.parent = self
            site.load()
        import_modules(self.settings.DJPCMS_PLUGINS)
        import_modules(self.settings.DJPCMS_WRAPPERS)
        return tuple(self)
    
    def make_url(self, route, handler, name=None):
        return (route, handler, name)
    
    def resolve(self, path, urlargs = None):
        with resolver_manager(self,path) as rm:
            for handler in self.urls():
                match = handler.rel_route.match(path)
                if match is None:
                    continue
                remaining_path = match.pop('__remaining__','')
                if urlargs:
                    urlargs.update(match)
                else:
                    urlargs = match
                if isinstance(handler,ResolverMixin):
                    return handler.resolve(remaining_path, urlargs)
                elif not remaining_path:
                    return handler, urlargs
                
            # Nothing found Check the static pages if they are available
            view = self.pageview(path)
            if view:
                return view, {}
            else:
                raise Http404(handler = self)
            
    def pageview(self, path):
        Page = self.root.Page
        if Page:
            from djpcms.views import pageview
            path = self.route + path
            try:
                return pageview(Page.objects.get(url = path.path),self)
            except page.DoesNotExist:
                pass
    
    def for_model(self, model):
        '''Obtain a :class:`djpcms.views.appsite.ModelApplication` for *model*.
If the application is not available, it returns ``None``. It never fails.'''
        return None
    
    def djp(self, request, path):
        '''Entry points for requests'''
        site, view, kwargs = self.resolve(path)
        return view(request, **kwargs)
    
    def make_parent(self, parent):
        parent = super(ResolverMixin,self).make_parent(parent)
        for route in self:
            route.parent = self
        return parent

    def on_bound(self):
        '''Callback when the resolver is bound'''
        pass
