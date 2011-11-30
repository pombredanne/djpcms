import os
import sys
import traceback
import logging
from copy import copy, deepcopy

from py2py3 import iteritems, itervalues

import djpcms
from djpcms import html
from djpcms.utils.importer import import_module, module_attribute
from djpcms.utils import conf, logtrace, closedurl, force_str, lazyproperty
from djpcms.utils.dispatch import Signal

from .exceptions import AlreadyRegistered, PermissionDenied,\
                        ImproperlyConfigured, DjpcmsException,\
                        Http404
from .urlresolvers import ResolverMixin
from .management import find_commands
from .permissions import PermissionHandler, SimpleRobots
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
                 robots = None,
                 parent = None):
        super(Site,self).__init__(route,parent)
        if not parent:
            settings = settings or get_settings()
            permissions = permissions or PermissionHandler()
            robots = robots or SimpleRobots()
        path = os.path.join(settings.SITE_DIRECTORY,'templates')
        if path not in settings.TEMPLATE_DIRS and os.path.isdir(path):
            settings.TEMPLATE_DIRS += path,
        path = os.path.join(djpcms.__path__[0],'media','djpcms')
        if path not in settings.TEMPLATE_DIRS:
            settings.TEMPLATE_DIRS += path,
        self._model_registry = {}
        self.plugin_choices = [('','-----------------')]
        if settings:
            self.internals['settings'] = settings
        if permissions:
            self.internals['permissions'] = permissions
        if robots:
            self.internals['robots'] = robots
        if response_handler:
            self.internals['response_handler'] = response_handler
        
    
    def render_response(self, response, callback = None):
        r = self.response_handler
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
                if isinstance(appurls,str):
                    appurls = module_attribute(appurls,safe=False)
            if hasattr(appurls,'__call__'):
                appurls = appurls()
            self.routes.extend((self._register_app(a) for a in appurls))
            
        self.internals['template'] = html.ContextTemplate(self)    
        return super(Site,self)._load()
    
    def addsite(self, settings = None, route = None, permissions = None):
        '''Add a new :class:`Site` to ``self``.

:parameter settings: Optional settings for the site.    
:parameter route: the base ``url`` for the site.
:parameter permission: An optional :ref:`site permission handler <permissions>`.
:rtype: an instance of :class:`Site`.
'''
        if self.isbound:
            raise ValueError('Cannot add a new site.')
        site = Site(settings = settings or self.settings, 
                    route = route or '',
                    permissions = permissions,
                    parent = self)
        self.routes.append(site)
        return site
    
    def for_model(self, model, all = False):
        '''Obtain a :class:`Application` for model *model*.
If the application is not available, it returns ``None``. Never fails.'''
        if not model:
            return
        if hasattr(model,'model'):
            model = model.model
        app = self.for_hash(model, safe = True)
        if app:
            return app
        model = mapper(model).model
        try:
            app = self._model_registry.get(model,None)
        except:
            app = None
        if not app and all:
            apps = tuple(self.root.for_model(model, exclude = self))
            if apps:
                #TODO. what about if there are more than one?
                return apps[0]
        else:
            return app
        
    def for_hash(self, model_hash, safe = True, all = False):
        '''Obtain a :class:`Application` for model
 model hash id. If the application is not available, it returns ``None``
 unless ``safe`` is set to ``False`` in which case it throw a
 :class:`djpcms.core.exceptions.ApplicationNotAvailable`.'''
        if model_hash in model_from_hash:
            model = model_from_hash[model_hash]
        else:
            if safe:
                return None
            else:
                raise ValueError('Model type %s not available' % model_hash)
        appmodel = self.for_model(model, all = all)
        if not appmodel:
            if not safe:
                raise ApplicationNotAvailable('Model {0} has\
 not application registered'.format(mapper(model)))
        return appmodel
    
    @lazyproperty
    def template_context(self):
        self.lock.acquire()
        mw = []
        try:
            for p_path in self.settings.TEMPLATE_CONTEXT_PROCESSORS:
                func = module_attribute(p_path,safe=True)
                if func:
                    mw.append(func)
            return tuple(mw)
        finally:
            self.lock.release()
    
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
        if not hasattr(self,'_commands'):
            self._commands = gc = {}
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
    
        return self._commands
    
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
