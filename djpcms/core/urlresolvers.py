import re
from inspect import isclass

from py2py3 import is_bytes_or_string, iteritems

from djpcms.utils import force_str, SLASH

from .exceptions import *
from . import http


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
        if isinstance(value,Http404) and not self.path.endswith(SLASH):
            try:
                v,u,k = self.resolver.resolve(self.path+SLASH)
            except:
                pass
            else:
                value.trypath = self.path+SLASH
        

class ResolverMixin(object):
    '''A lazy class for resolving urls.
The main function here is the ``resolve`` method'''
    def load(self):
        '''Load urls and set-up sites'''
        if getattr(self,'_urls',None) is None:
            self._urls = self._load()
        
    def __get_isloaded(self):
        return getattr(self,'_urls',None) is not None
    isloaded = property(__get_isloaded)
    
    def urls(self):
        self.load()
        return self._urls
    
    def _load(self):
        pass
        
    def clear(self):
        pass
    
    def clean_path(self, environ):
        '''Clean url and redirect if needed
        '''
        path = environ['PATH_INFO']
        if '//' in path:
            url = re.sub("/+" , SLASH, path)
            if not url.startswith(SLASH):
                url = '/%s' % url
            qs = environ['QUERY_STRING']
            if qs and environ['method'] == 'GET':
                url = '{0}?{1}'.format(url,qs)
            return http.ResponseRedirect(url)
    
    def make_url(self, regex, view, kwargs=None, name=None):
        return RegexURLPattern(regex, view, kwargs, name)
    
    @property
    def resolver(self):
        if not hasattr(self,'_resolver'):
            self._resolver = RegexURLResolver(r'^', self.urls())
        return self._resolver
    
    def resolve(self, path):
        # try sitemap first
        spath = SLASH+path
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


class RegexURLResolver(object):
    """\
This class ``resolve`` method takes a URL (as a string) and returns a
tuple in this format:

    (view_function, function_args, function_kwargs)
    
Adapted from django for djpcms
"""
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




