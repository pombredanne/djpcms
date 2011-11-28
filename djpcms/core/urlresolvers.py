import re
from inspect import isclass

from py2py3 import is_bytes_or_string, iteritems

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

    proxy to :attr:`Route.path` attribute of :attr:`route`
    
.. attribute:: root

    The root :class:`RouteMixin` instance for of this route.    
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
                raise ValueError('parent must be an instance of RouteMixin.')
            self.__route = parent.route + self.__rel_route
        else:
            self.__route = self.__rel_route
        return parent
    
    
    
class ResolverMixin(RouteMixin):
    '''Mixin for classes with several routes.'''
    def __init__(self, route, parent = None):
        if not isinstance(route,Route):
            route = Route(route, append_slash = True)
        if route.is_leaf:
            raise ValueError('A resolver cannot have a leaf route {0}'\
                             .format(route))
        super(ResolverMixin,self).__init__(route,parent)
        self.routes = OrderedDict()
        
    def __len__(self):
        return len(self.routes)
    
    def count(self):
        return len(self.routes)
    
    def __iter__(self):
        return self.routes.__iter__()
    
    def load(self):
        '''Load urls and set-up sites'''
        if not hasattr(self,'_urls'):
            self._urls = self._load()
        
    @property
    def isloaded(self):
        return hasattr(self,'_urls')
    
    def urls(self):
        self.load()
        return self._urls
    
    def _load(self):
        if not self.routes:
            raise ImproperlyConfigured('No sites registered.')
        settings = self.settings
        sites = self.all()
        if sites[-1].route.rule is not '':
            raise ImproperlyConfigured('There must be a root site available.')
        for site in sites:
            site.load()
        import_modules(settings.DJPCMS_PLUGINS)
        import_modules(settings.DJPCMS_WRAPPERS)
        urls = []
        for site in sites:
            route = site.rel_route + '<path>/'
            name = getattr(site,'name',None)
            urls.append(self.make_url(route, site, name = name))
        return tuple(urls)
    
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
    
    def make_url(self, route, view, kwargs=None, name=None):
        return (regex, view, kwargs, name)
    
    @property
    def resolver(self):
        if not hasattr(self,'_resolver'):
            self._resolver = RouteResolver(r'^', self.urls())
        return self._resolver
    
    def resolve(self, path):
        # try sitemap first
        spath = '/'+path
        site = None
        node = None
        try:
            node = self.tree[spath]
            return self.resolve_from_node(node)
        except KeyError:
            pass
        
        view = self
        rurl = (path,)
        urlargs = {}
        with resolver_manager(self,path) as rm:
            while isinstance(view,ResolverMixin):
                if len(rurl) != 1:
                    if 'path' not in urlargs:
                        raise Http404(site = site)
                    bit = urlargs.pop('path')
                else:
                    bit = rurl[0]
                try:
                    view, rurl, kwargs = view.resolver.resolve(bit)
                except Resolver404 as e:
                    if not urlargs:
                        try:
                            node = self.tree.node(spath, site = site)
                            return self.resolve_from_node(node)
                        except PathException:
                            raise Http404(str(e),site = site)
                    else:
                        raise Http404(str(e),site = site)
                
                if site is None:
                    site = view
                urlargs.update(kwargs)
        
        return site, view, urlargs
            
    def resolve_from_node(self, node):
        site = node.site
        try:
            view = node.get_view()
            return view.site,view,{}
        except PathException as e:
            raise Http404(str(e), site = site)
    
    def for_model(self, model):
        '''Obtain a :class:`djpcms.views.appsite.ModelApplication` for *model*.
If the application is not available, it returns ``None``. It never fails.'''
        return None
    
    def djp(self, request, path):
        '''Entry points for requests'''
        site, view, kwargs = self.resolve(path)
        return view(request, **kwargs)  


class RegexURLPattern(object):
    """ORIGINAL CLASS FROM DJANGO    www.djangoproject.com

Adapted for djpcms
"""
    def __init__(self, regex, callback,
                 default_args=None,
                 name=None):
        # regex is a string representing a regular expression.
        # callback is either a string like 'foo.views.news.stories.story_detail'
        # which represents the path to a module and a view function name, or a
        # callable object (view).
        self.regex = re.compile(regex, re.UNICODE)
        self.callback = callback
        self.default_args = default_args or {}
        self.name = name

    def __repr__(self):
        return '<%s %s %s>' % (self.__class__.__name__, self.name,
                               self.regex.pattern)

    def resolve(self, path):
        match = self.regex.search(path)
        if match:
            # If there are any named groups, use those as kwargs, ignoring
            # non-named groups. Otherwise, pass all non-named arguments as
            # positional arguments.
            kwargs = match.groupdict()
            if kwargs:
                args = ()
            else:
                args = match.groups()
            # In both cases, pass any extra_kwargs as **kwargs.
            kwargs.update(self.default_args)

            return self.callback, args, kwargs


class RouteResolver(object):
    """Resulve routes"""
    def __init__(self, regex, url_patterns, default_kwargs=None):
        # regex is a string representing a regular expression.
        # urlconf_name is a string representing the module containing URLconfs.
        self.regex = re.compile(regex, re.UNICODE)
        self.url_patterns = url_patterns
        self.callback = None
        self.default_kwargs = default_kwargs or {}

    def resolve(self, path):
        tried = []
        match = self.regex.search(path)
        if match:
            new_path = path[match.end():]
            for pattern in self.url_patterns:
                try:
                    sub_match = pattern.resolve(new_path)
                except Resolver404 as e:
                    sub_tried = e.args[0].get('tried')
                    if sub_tried is not None:
                        tried.extend([(pattern.regex.pattern + '   ' + t)\
                                       for t in sub_tried])
                    else:
                        tried.append(pattern.regex.pattern)
                else:
                    if sub_match:
                        sub_match_dict = dict([(force_str(k), v)\
                                     for k, v in match.groupdict().items()])
                        sub_match_dict.update(self.default_kwargs)
                        for k, v in iteritems(sub_match[2]):
                            sub_match_dict[force_str(k)] = v
                        return sub_match[0], sub_match[1], sub_match_dict
                    tried.append(pattern.regex.pattern)
            raise Resolver404({'tried': tried, 'path': new_path})
        raise Resolver404({'path' : path})




