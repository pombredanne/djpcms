import re
from inspect import isclass
from copy import copy, deepcopy

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
    '''Class for routing trees
    
.. attribute:: parent

    The :class:`RouteMixin` immediately before this route.
    
.. attribute:: route

    The :class:`Route` for this instance
    
.. attribute:: rel_route

    The relative :class:`Route` with respect :attr:`parent` for this instance.
    
.. attribute:: path

    proxy to the :attr:`Route.path` attribute of :attr:`route`.
    It is the absolute path for this instance.
    
.. attribute:: root

    The root :class:`RouteMixin` instance for of this route. If this instance
    has :attr:`parent` set to ``None``, the :attr:`root
    
.. attribute:: settings

    web site settings dictionary
'''
    def __init__(self, route, parent = None):
        if not isinstance(route,Route):
            route = Route(route)
        self.__rel_route = route
        self.__route = route
        self.parent = parent
        self.internals = {}
        
    def __unicode__(self):
        return self.route.rule
        
    def _get_parent(self):
        return self.__parent
    def _set_parent(self, parent):
        self.__parent = self.make_parent(parent)
    parent = property(_get_parent,_set_parent)
    
    @property
    def route(self):
        return self.__route
    
    @property
    def path(self):
        return self.route.path
    
    @property
    def rel_route(self):
        return self.__rel_route
    
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
                if self.isbound:
                    raise ValueError('parent must be an instance of RouteMixin.\
 Got "{0}"'.format(parent))
                else:
                    return parent
            self.__route = parent.route + self.__rel_route
        else:
            self.__route = self.__rel_route
        return parent
    
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
        self.routes = OrderedDict()
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
        return iter(itervalues(self.routes))
    
    def __getitem__(self, index):
        return list(self)[index]
    def __setitem(self, index, val):
        raise TypeError('Site object does not support item assignment')
    
    def load(self):
        '''Load urls and set-up sites'''
        if not hasattr(self,'_urls'):
            self._urls = self._load()
        
    def _isbound(self):
        return hasattr(self,'_urls')
    
    def urls(self):
        self.load()
        return self._urls
    
    def _load(self):
        if not self.routes:
            raise ImproperlyConfigured('No sites registered.')
        for site in self:
            site.load()
        import_modules(self.settings.DJPCMS_PLUGINS)
        import_modules(self.settings.DJPCMS_WRAPPERS)
        return tuple(self)
    
    def clean_path(self, environ):
        '''Clean url and redirect if needed
        '''
        path = environ['PATH_INFO']
        if '//' in path:
            url = re.sub("/+" , '/', path)
            if not url.startswith('/'):
                url = '/%s' % url
            qs = environ['QUERY_STRING']
            if qs and environ['method'] == 'GET':
                url = '{0}?{1}'.format(url,qs)
            return http.ResponseRedirect(url)
    
    def make_url(self, route, handler, name=None):
        return (route, handler, name)
    
    def resolve(self, path):
        with resolver_manager(self,path) as rm:
            for handler in self.urls():
                match = handler.route.match(bit)
                if match is not None:
                    break
            if match is None:
                raise Http404(handler = self)
            path = match.pop('__remaining__',None)
            if isinstance(handler,ResolverMixin):
                return handler.resolve(path or '')
            elif path:
                raise Http404(handler = self)
            else:
                return handler, match
    
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

