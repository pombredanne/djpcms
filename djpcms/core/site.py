import os
import sys
import traceback
import logging
from copy import copy, deepcopy
from threading import Lock

from py2py3 import iteritems, itervalues

import djpcms
from djpcms import html
from djpcms.utils.importer import import_module, module_attribute
from djpcms.utils import conf, logtrace, closedurl, force_str
from djpcms.utils.dispatch import Signal

from .exceptions import AlreadyRegistered, PermissionDenied,\
                        ImproperlyConfigured, DjpcmsException,\
                        Http404
from .urlresolvers import ResolverMixin
from .management import find_commands
from .permissions import PermissionHandler
from . import http
from . import orms

__all__ = ['SiteLoader', 'Site', 'get_settings']


logger = logging.getLogger('djpcms')



def default_response_handler(djp, response, callback = None):
    if isinstance(response,dict):
        rr = default_response_handler
        response = dict(((k,rr(djp,v)) for k,v in iteritems(response)))
    elif isinstance(response,html.ContextRenderer):
        response = response.render()
    return callback(response) if callback else response


def get_settings(name = None, settings = None, **params):
    '''Extra configuration parameters,can be passed as key-value pairs:

:parameter name: file or directory name which specifies the
             application root-directory.
             
:parameter settings: optional settings file name specified as a dotted path
relative ro the application directory.

Default ``None``

:parameter params: key-value pairs which override the values
               in the settings file.
'''
    name = name if name is not None else os.getcwd()
    if os.path.isdir(name):
        appdir = name
    elif os.path.isfile(name):
        appdir = os.path.split(os.path.realpath(name))[0]
    else:
        try:
            mod = import_module(name)
            appdir = mod.__path__[0]
        except ImportError:
            raise ValueError(
                    'Could not find directory or file {0}'.format(name))
    site_path = os.path.realpath(appdir)
    base,name = os.path.split(site_path)
    if base not in sys.path:
        sys.path.insert(0, base)
    
    # Import settings
    if settings:
        if '.' in settings:
            settings_module_name = settings
        else:
            sett = '{0}.py'.format(os.path.join(site_path,settings))
            if os.path.isfile(sett):
                settings_module_name = '{0}.{1}'.format(name,settings)
            else:
                settings_module_name = settings
    else:
        settings_module_name = None
    
    return conf.get_settings(settings_module_name,
                             SITE_DIRECTORY = site_path,
                             SITE_MODULE = name,
                             **params)


class TreeUpdate(object):
    
    def __init__(self, sites):
        self.sites = sites
        if self.sites.Page:
            self.sites.Page.register_tree_update(self)
        
    def __call__(self, sender, instance = None, **kwargs):
        '''Register the page post save with tree'''
        if isinstance(instance, self.sites.Page):
            self.sites.tree.update_flat_pages()


class SiteLoader(object):
    '''An utility class for loading and configuring djpcms sites.
 
 .. attribute:: name
 
     The configuration name, useful when different types of configuration are
     needed (WEB, RPC, ...)
'''
    ENVIRON_NAME = None
    settings = None
    
    def __init__(self, name = None, route = '/', **params):
        self.sites = None
        self._wsgi_middleware = None
        self._response_middleware = None
        self.name = name or 'DJPCMS'
        self.route = route
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
            self.sites = Site(self.route)
            if self.ENVIRON_NAME:
                os.environ[self.ENVIRON_NAME] = self.name
            name = '_load_{0}'.format(self.name.lower())
            getattr(self,name,self.default_load)()
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
    
    def default_load(self):
        '''Default loading'''
        self.sites.make(os.getcwd(),
                        settings = self.settings)
        
    def finish(self):
        '''Callback once the sites are loaded.'''
        pass
    
    def on_server_ready(self, server):
        '''Optional callback by a server just before start serving.'''
        pass

    def wsgi(self):
        return http.WSGIhandler(self.wsgi_middleware(),
                                self.response_middleware())
        
    
def standard_exception_handle(request, e, status = None):
    status = status or getattr(e,'status',None) or 500
    info = request.DJPCMS
    site = info.site
    settings = site.settings
    exc_info = sys.exc_info()
    if site is None:
        raise
    template = '{0}.html'.format(status)
    template2 = 'errors/{0}'.format(template)
    template3 = 'djpcms/{0}'.format(template2)
    
    logtrace(logger, request, exc_info, status)
    #store stack trace in the DJPCMS environment variable
    info.stack_trace = traceback.format_exception(*exc_info)
    stack_trace = '<p>{0}</p>'.format('</p>\n<p>'.join(info.stack_trace))
    ctx = {'status':status,
           'status_text':http.STATUS_CODE_TEXT.get(status,
                                http.UNKNOWN_STATUS_CODE)[0],
           'stack_trace':stack_trace,
           'settings':site.settings}
    html = site.template.render(
                (template,template2,template3,'djpcms/errors/error.html'),
                 ctx,
                 request = request,
                 encode = 'latin-1',
                 encode_errors = 'replace')
    return http.Response(status = status,
                         content = html,
                         content_type = 'text/html',
                         encoding = settings.DEFAULT_CHARSET)
    
    
class Site(ResolverMixin):
    '''A :class:`ResolverMixin` holding other :class:`Site` instances
and :class:`djpcms.views.Application` instances::

    import djpcms
    site = djpcms.Site()

:parameter settings: optional settings instance for
    :attr:`RouteMixin.settings` attribute.
        
:parameter route: optional base route for
    :attr:`RouteMixin.route` attribute.
    
:parameter response_handler: optional function for handling responses.


Attributes available:
    
.. attribute:: search_engine

    An instance of a search engine interface
    
.. attribute:: User

    The user model used by the site
    
'''
    profilig_key = None
    
    def __init__(self,
                 settings = None,
                 route = '/',
                 permissions = None,
                 response_handler = None,
                 parent = None):
        super(Site,self).__init__(route,parent)
        if parent:
            settings = settings or parent.settings
            permissions = permissions or parent.permissions
            response_handler = response_handler or\
                                 parent.internals['response_handler']
        else:
            settings = settings or get_settings()
            permissions = permissions or PermissionHandler()
        path = os.path.join(settings.SITE_DIRECTORY,'templates')
        if path not in settings.TEMPLATE_DIRS and os.path.isdir(path):
            settings.TEMPLATE_DIRS += path,
        path = os.path.join(djpcms.__path__[0],'media','djpcms')
        if path not in settings.TEMPLATE_DIRS:
            settings.TEMPLATE_DIRS += path,
        self._model_registry = {}
        self.plugin_choices = [('','-----------------')]
        self.internals['settings'] = settings
        self.internals['response_handler'] = response_handler
        self.internals['permissions'] = permissions
        self.internals['handle_exception'] = standard_exception_handle
        self.internals['events'] = {'on_site_loaded': Signal(),
                                    'request_started': Signal(),
                                    'start_response': Signal(),
                                    'request_finished': Signal()}
    
    @property
    def events(self):
        return self.internals['events']
    
    def render_response(self, response, callback = None):
        r = self.internals['response_handler']
        if r:
            return r(self, response, callback = callback)
        else:
            return default_response_handler(self, response, callback)
    
    def unwind_query(self, query, callback = None):
        '''query is an instance of :class:`djpcms.orms.OrmQuery`'''
        r = self.internals['response_handler']
        if r:
            return r(self, query, callback = callback)
        else:
            return callback(query.query) if callback else query.query
        
    def _load(self):
        if self.root == self:
            if not self and not self.settings:
                raise ImproperlyConfigured('Site has no routes registered and\
 no settings.')
            from .sitemap import SiteMap
            self.internals['tree'] = tree = SiteMap(self)
            for wrapper in orms.model_wrappers.values():
                wrapper.setup_environment(self)
                
        appurls = self.settings.APPLICATION_URLS
        if appurls:
            if not hasattr(appurls,'__call__'):
                if is_bytes_or_string(appurls):
                    appurls = module_attribute(appurls,safe=False)
            if hasattr(appurls,'__call__'):
                appurls = appurls()
            self.routes.update(((a.rel_route.path,self._register_app(a))
                                 for a in appurls))
            
        self.template = html.ContextTemplate(self)    
        urls = super(Site,self)._load()
        self.events['on_site_loaded'].send(self)
        #self._tree_updated = TreeUpdate(self)
        return urls
    
    def addsite(self, settings = None, route = None, permissions = None):
        '''Create a new ``djpcms`` :class:`djpcms.views.ApplicationSite`.
    
:parameter route: the base ``url`` for the site applications.

    Default ``None``
    
:parameter permission: An optional :ref:`site permission handler <permissions>`.
:rtype: an instance of :class:`djpcms.views.ApplicationSite`.
'''
        site = Site(settings = settings or self.settings, 
                    route = route or '',
                    permissions = permissions,
                    parent = self)
        if site.path in self.routes:
            raise AlreadyRegistered('Site with path {0}\
 already avalable.'.format(site.path))
        self.routes[site.path] = site
        self.__dict__.pop('_urls',None)
        return site
    
    def get(self, name, default = None):
        return self._sites.get(name,default)
            
    def get_site(self, url = None):
        url = url or '/'
        site = self.get(url,None)
        if not site:
            try:
                res = self.resolve(url[1:])
                return res[0]
            except Http404:
                return None
        else:
            return site
        
    def get_urls(self):
        urls = []
        for site in self.values():
            urls.extend(site.get_urls())
        return urls
     
    def get_url(self, model, view_name, instance = None, url = None, **kwargs):
        site = self.get_site(url)
        if not site:
            return None
        return site.get_url(model, view_name, instance = None, **kwargs)
        if not isinstance(model,type):
            instance = model
            model = instance.__class__
        app = site.for_model(model)
        if app:
            view = app.getview(view_name)
            if view:
                try:
                    return view.get_url(None, instance = instance, **kwargs)
                except:
                    return None
        return None
    
    def view_from_page(self, page):
        site = self.get_site(page.url)
    
    def for_model(self, model, exclude = None):
        if not model:
            raise StopIteration
        for site in self.all():
            if site is not exclude:
                r2 = site.for_model(model)
                if r2:
                    yield r2
    
    def setsettings(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self.settings,k,v)
            for site in self:
                setattr(site.settings,k,v)
            
    def get_commands(self):
        gc = self._commands
        if gc is None:
            gc = self._commands = {}
            # Find and load the management module for each installed app.
            for app_name in self.settings.INSTALLED_APPS:
                if app_name.startswith('django.'):
                    continue
                command_module = app_name
                if app_name == 'djpcms':
                    command_module = 'djpcms.core'
                try:
                    mod = import_module(command_module+'.management')
                    if hasattr(mod,'__path__'):
                        path = mod.__path__[0]
                        gc.update(dict(((name, command_module)
                                        for name in find_commands(path))))
                except ImportError:
                    pass # No management module
    
        return gc
    
    def registered_models(self):
        '''Generator of model Choices'''
        p = set()
        for site in self.all():
            for model in site._registry:
                if model not in p:
                    p.add(model)
                    yield model
    
    def _register_app(self, application, parent = None):
        if not isinstance(application,ResolverMixin):
            raise ImproperlyConfigured('Cannot register application.\
 Is is not a valid one.')
        
        application.parent = self
        
        if isinstance(application,Site):
            return application
        
        model = application.model
        if model:
            if model in self._model_registry:
                raise AlreadyRegistered('Model %s already registered\
 as application' % model)
            self._model_registry[model] = application
            
        # Handle parent application if available
        if parent:
            parent_view = application.parent
            if not parent_view:
                parent_view = parent.root_view
            elif parent_view not in parent.views:
                raise ApplicationUrlException("Parent {0} not available\
 in views.".format(parent))
            else:
                parent_view = parent.views[parent_view]
            application.parent = parent_view
            application.baseurl = parent_view.baseurl +\
                                             parent_view.regex + \
                                             application.baseurl
        else:
            application.parent = self
            
        # Create application views
        application.load()
        return application
