import re
from inspect import isclass
from copy import copy, deepcopy
from threading import Lock

from djpcms.utils.py2py3 import UnicodeMixin, is_bytes_or_string, iteritems,\
                                itervalues
from djpcms.utils.structures import OrderedDict
from djpcms.utils.importer import import_modules

from .exceptions import *
from .routing import Route
from .tree import NRT
from .permissions import VIEW
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
        path = self.path
        if path and isinstance(value,Http404) and not path.endswith('/'):
            path = path+'/'
            try:
                v,u = self.resolver.resolve(path)
            except:
                pass
            else:
                value.trypath = '/'+path
    
    
class RouteMixin(UnicodeMixin):
    '''Class for routing trees. This class is the base class for all
routing and handler classes in djpcms including, but not only, :class:`Site`,
:class:`djpcms.views.Application` and :class:`djpcms.views.View`.
    
:parameter route: A :class:`Route` instance or a route string, it is used
    to set the :attr:`rel_route` attribute.
    
:parameter parent: It sets the :attr:`parent` attribute.

    Default: ``None``.
    

--


**Attributes**

    
.. attribute:: parent

    The :class:`RouteMixin` immediately before this route. When setting
    this attribute, the :attr:`route` is updated from the :attr:`rel_route`
    attribute as ``self`` and the :attr:`route` of :attr:`parent`.
    
.. attribute:: rel_route

    The relative :class:`Route` with respect :attr:`parent` for this instance.
    
.. attribute:: route

    The :class:`Route` for this instance. Calculated from :attr:`rel_route`
    and :attr:`parent`.
    
.. attribute:: path

    proxy to the :attr:`Route.path` attribute of :attr:`route`.
    It is the absolute path for this instance.
    
.. attribute:: isbound

    ``True`` when the route is bound to a :class:`ResolverMixin` instance.
    
.. attribute:: root

    The root :class:`RouteMixin` instance for of this route. If this instance
    has :attr:`parent` set to ``None``, the :attr:`root` is equal to ``self``.
    
.. attribute:: is_root

    ``True`` if :attr:`root` is ``self``.
    
.. attribute:: tree

    The views non-recombining tree
    
.. attribute:: site

    The closes :class:`Site` instance for of this route.
    
.. attribute:: settings

    web site settings dictionary, available when :attr:`isbound` is ``True``.
'''
    PERM = VIEW
    
    def __new__(cls, *args, **kwargs):
        o = super(RouteMixin,cls).__new__(cls)
        o._local = {}
        return o
    
    def __init__(self, route, parent = None):
        if not isinstance(route,Route):
            route = Route(route)
        self.__rel_route = route
        self.parent = parent
        self.internals = {}
        
    def __unicode__(self):
        return self.route.rule
    
    def __deepcopy__(self, memo):
        o = self.__class__.__new__(self.__class__)
        memo[id(self)] = o
        d = self.__dict__.copy()
        d.pop('_local',None)
        o._local = {}
        d = self._oncopy(d)
        for attr,value in d.items():
            if not isclass(value):
                try:
                    value = deepcopy(value, memo)
                except TypeError:
                    pass
            setattr(o, attr, value)
        return o
    
    def __getstate__(self):
        '''Remove the local dictionary.'''
        d = self.__dict__.copy()
        d.pop('_local')
        return d
    
    @property
    def local(self):
        return self._local
    
    @property
    def lock(self):
        if 'lock' not in self.local:
            self.local['lock'] = Lock()
        return self.local['lock']
    
    @property
    def route(self):
        if 'route' not in self._local:
            self._local['route'] = self.rel_route 
        return self._local['route']
    
    def _get_parent(self):
        return self._local.get('parent')
    def _set_parent(self, parent):
        if parent is not self.parent:
            self._local['parent'] = self._make_parent(parent)
    parent = property(_get_parent,_set_parent)
    
    def __get_rel_route(self):
        return self.__rel_route
    def __set_rel_route(self, r):
        if self.route == self.__rel_route:
            self.__rel_route = r
            self._local['route'] = r
        else:
            br = self.route - self.rel_route
            self.__rel_route = r
            self._local['route'] = br + r
    rel_route = property(__get_rel_route,__set_rel_route)
    
    @property
    def site(self):
        return self._site()
    
    @property
    def is_root(self):
        return self.parent is None
    
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
    def tree(self):
        if self.is_root:
            return self.local.get('tree')
        else:
            self.root.tree
    
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
    def response(self):
        '''Access the site :ref:`response handler <response-handler>`.'''
        return self.internal_data('response_handler')
    
    @property
    def settings(self):
        return self.internal_data('settings')
    
    @property
    def search_engine(self):
        return self.internal_data('search_engine')
    
    @property
    def permissions(self):
        return self.internal_data('permissions')
    
    @property
    def meta_robots(self):
        return self.internal_data('meta_robots')
    
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
    
    def encoding(self, request):
        '''Encoding for this route'''
        return self.settings.DEFAULT_CHARSET
    
    def cssgrid(self, request):
        settings = self.settings
        page = request.page
        layout = page.layout if page else None
        layout = layout or settings.LAYOUT_GRID_SYSTEM
        return get_cssgrid(layout)
    
    def instance_from_variables(self, environ, urlargs):
        '''Retrieve an instance form the variable part of the
 :attr:`route` attribute.
 
 :parameter urlargs: dictionary of url arguments.
 
 This function needs to be implemented by subclasses. By default it returns
 ``None``.
 '''
        pass
    
    def variables_from_instance(self, instance):
        '''Retrieve the url bits from an instance. It returns an iterator
 over key-value touples or a dictionary. This is the inverse of
 :meth:`instance_from_variables` function.'''
        raise StopIteration
    
    def get_url(self, urlargs, instance = None):
        '''Retrieve the :attr:`route` full *url* from a dictionary of
url attributes and, optionally, an instance of an element constructed
from the variable part of the url.'''
        if instance:
            urlargs.update(self.variables_from_instance(instance))
        try:
            return self.route.url(**urlargs)
        except:
            return None
    
    ############################################################################
    #    INTERNALS
    ############################################################################
    
    def _oncopy(self, d):
        return d
    
    def _make_parent(self, parent):
        if parent is not None:
            if not isinstance(parent, RouteMixin):
                raise ValueError('parent must be an instance of RouteMixin.\
 Got "{0}"'.format(parent))
            self.local['route'] = parent.route + self.__rel_route
        else:
            self.local['route'] = self.__rel_route
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
            raise ImproperlyConfigured('No sites registered.')
        for route in self:
            if route.isbound:
                raise ImproperlyConfigured('Route {0} already bound.'\
                                           .format(route))
            route.parent = self
            route.load()
        import_modules(self.settings.DJPCMS_PLUGINS)
        import_modules(self.settings.DJPCMS_WRAPPERS)
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
                    
    def resolve(self, path, urlargs = None):
        '''Resolve a path'''            
        with resolver_manager(self,path) as rm:
            urlargs = urlargs if urlargs is not None else {}
            for handler in self.urls():
                match = handler.rel_route.match(path)
                if match is None:
                    continue
                remaining_path = match.pop('__remaining__','')
                urlargs.update(match)
                if isinstance(handler,ResolverMixin):
                    res = handler.resolve(remaining_path, urlargs)
                    if res:
                        return res
                elif not remaining_path:
                    return handler, urlargs
                
            # Nothing found Check the static pages if they are available
            if self.is_root:
                raise Http404(path, handler = self)
                path = self.route + path
                view = self.pageview(path)
                if view:
                    return view, {}
                else:
                    raise Http404(path, handler = self)
            
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
        parent = super(ResolverMixin,self)._make_parent(parent)
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
