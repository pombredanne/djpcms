import os
import sys
import logging
import argparse
from inspect import isclass
from copy import deepcopy, copy

from djpcms.utils.py2py3 import iteritems, itervalues, native_str
from djpcms.utils.importer import import_module, module_attribute,\
                                  import_modules
from djpcms.utils import conf, lazyproperty, Path
from djpcms.utils.structures import OrderedDict
from djpcms import html

from .exceptions import AlreadyRegistered, PermissionDenied,\
                        ImproperlyConfigured, DjpcmsException,\
                        Http404
from .urlresolvers import ResolverMixin
from .management import find_commands
from .permissions import PermissionHandler, SimpleRobots
from .cache import CacheHandler
from .async import ResponseHandler
from . import http
from . import orms
from . import layout


__all__ = ['Site', 'ViewRenderer', 'get_settings', 'WebSite']


logger = logging.getLogger('djpcms')


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
    name = Path(name if name is not None else os.getcwd())
    if name.isdir():
        appdir = name
    elif name.isfile():
        appdir = name.realpath().parent
    else:
        try:
            mod = import_module(name)
            appdir = Path(mod.__path__[0])
        except ImportError:
            raise ValueError(
                    'Could not find directory or file {0}'.format(name))
    site_path = appdir.realpath()
    base, name = site_path.split()
    if base not in sys.path:
        sys.path.insert(0, str(base))
    
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
    
    return conf.Config(settings_module_name,
                       SITE_DIRECTORY = site_path,
                       SITE_MODULE = name,
                       **params)


DEFAULT_SITE_HANDLERS = {
    'response_handler': ResponseHandler(),
    'permissions': PermissionHandler,
    'meta_robots': SimpleRobots,
    'cache': CacheHandler()
}


def add_default_handlers(site):
    internals = site.internals
    for key,value in DEFAULT_SITE_HANDLERS.items():
        handler = internals.get(key)
        if handler is None:
            if isclass(value):
                value = value(site.settings)
            internals[key] = value
            

class ViewRenderer(html.Renderer):
    appmodel = None
    inherit_page = False
    
    def parent_instance(self, instance):
        '''Return the parent instance for *instance*. This is the instance
for the parent view. By default it returns *instance*. This function
is used by the :attr:`djpcms.Request.parent` attribute.'''
        return instance
        
        
class Site(ResolverMixin, ViewRenderer):
    '''A :class:`ResolverMixin` holding other :class:`Site` instances
and :class:`djpcms.views.Application` instances::

    import djpcms
    site = djpcms.Site()

:parameter settings: optional settings instance for
    :attr:`RouteMixin.settings` attribute.
        
:parameter route: optional base route for
    :attr:`RouteMixin.route` attribute.
    
:parameter parent: optional instance of a parent :class:`Site` instance.

:parameter handlers: dictionary of :ref:`site handlers <site-handlers>`
    which will be added to the :attr:`internal` dictionary.


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
                 parent = None,
                 **handlers):
        super(Site, self).__init__(route)
        self._model_registry = {}
        self._page_layout_registry = OrderedDict()
        self.plugin_choices = [('','-----------------')]
        if parent is None:
            settings = settings or get_settings()
        else:
            self.parent = parent
        if settings:
            path = os.path.join(settings.SITE_DIRECTORY,'templates')
            if path not in settings.TEMPLATE_DIRS and os.path.isdir(path):
                settings.TEMPLATE_DIRS += path,
            self.internals['settings'] = settings
        self.internals.update(handlers)
        self.register_page_layout('default', layout.page())
        
    def setup_environment(self):
        '''Set up the the site.'''
        if self.root == self:
            for wrapper in orms.model_wrappers.values():
                wrapper.setup_environment(self)
            add_default_handlers(self)
        appurls = self.settings.APPLICATION_URLS
        if appurls:
            if not hasattr(appurls,'__call__'):
                if isinstance(appurls,str):
                    appurls = module_attribute(appurls,safe=False)
            if hasattr(appurls,'__call__'):
                appurls = appurls(self)
            self.routes.extend(deepcopy(appurls))
        return len(self)
    
    def _load(self):
        self.setup_environment()
        urls = super(Site, self)._load()
        import_modules(self.settings.DJPCMS_PLUGINS)
        import_modules(self.settings.DJPCMS_WRAPPERS)
        return urls
    
    def _site(self):
        return self
    
    def addsite(self, settings = None, route = None, **handlers):
        '''Add a new :class:`Site` to ``self``.

:parameter settings: Optional settings for the site.    
:parameter route: the base ``url`` for the site.
:parameter permission: An optional :ref:`site permission handler <permissions>`.
:rtype: an instance of :class:`Site`.
'''
        if self.isbound:
            raise ValueError('Cannot add a new site.')
        site = Site(settings = settings, 
                    route = route or '',
                    parent = self,
                    **handlers)
        self.routes.append(site)
        return site
    
    def for_model(self, model, all = False, start = True):
        '''Obtain a :class:`Application` for model *model*.
If the application is not available, it returns ``None``. It never fails.
If *all* is set to ``True`` it returns a list of all the :class:`Application`
for that model.'''
        if not model:
            return
        if hasattr(model,'model'):
            model = model.model
        mapper = orms.mapper(model)
        if not mapper:
            return None
        model = mapper.model
        app = self._model_registry.get(model)
        if not app or all:
            apps = [app] if app is not None else []
            for site in self:
                if not isinstance(site,Site):
                    break
                app = site.for_model(model,all)
                if app is not None:
                    if all:
                        apps.extend(app)
                    else:
                        return app
            if all:
                if start and self.parent:
                    for a in self.parent.for_model(model,all=True,start=False):
                        if a not in apps:
                            apps.append(a)
                return apps
        else:
            return app
        
    def for_hash(self, model_hash, safe = True, all = False):
        '''Obtain a :class:`Application` for model
 model hash id. If the application is not available, it returns ``None``
 unless ``safe`` is set to ``False`` in which case it throw a
 :class:`djpcms.core.exceptions.ApplicationNotAvailable`.'''
        if model_hash in orms.model_from_hash:
            model = orms.model_from_hash[model_hash]
        else:
            if safe:
                return None
            else:
                raise ValueError('Model type %s not available' % model_hash)
        app = self.for_model(model, all = all)
        if not app:
            if not safe:
                raise ApplicationNotAvailable('Model {0} has\
 not application registered'.format(orms.mapper(model)))
        return app
    
    @lazyproperty
    def request_context(self):
        self.lock.acquire()
        mw = []
        try:
            for p_path in self.settings.REQUEST_CONTEXT_PROCESSORS:
                func = module_attribute(p_path,safe=True)
                if func:
                    mw.append(func)
            return tuple(mw)
        finally:
            self.lock.release()
    
    def children(self, request):
        '''return a generator over children. It uses the
:func:`djpcms.node` to retrieve the node in the sitemap and
consequently its children.'''
        urlargs = request.urlargs
        for handler in self:
            try:
                path = handler.rel_route.url(**urlargs)
            except:
                continue
            view, nargs = handler.resolve(path)
            if not view.object_view:
                yield request.for_view(view, **nargs)
    
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

    def register_app(self, application):
        model = application.model
        if model:
            if model in self._model_registry:
                raise AlreadyRegistered('Model %s already registered\
 as application' % model)
            self._model_registry[model] = application
    
    def context(self, data, request = None, processors=None):
        '''Evaluate the context for the template. It returns a dictionary
which updates the input ``dictionary`` with library dependent information.
        '''
        data = data or {}
        if request:
            cache = request.cache
            if 'context' not in cache:
                context_cache = {}
                processors = self.request_context
                if processors is not None:
                    for processor in processors:
                        context_cache.update(processor(request))
                cache['context'] = context_cache
            data.update(cache['context'])
            data['request'] = request
        return data
            
    def applications(self):
        sites = []
        for app in self:
            if isinstance(app,Site):
                sites.append(app)
            else:
                yield app
                for app in app.applications():
                    yield app
                
        for site in sites:
            for app in site.applications():
                yield app
                
    def clear_model_tables(self):
        pass
    
    def create_model_tables(self):
        pass
    
    def register_page_layout(self, name, page):
        '''Register a :class:`djpcms.html.layout.page` with the
:class:`Site`. Return self for concatenating calls.'''
        name = name.lower()
        self._page_layout_registry[name] = page
        return self
    
    def get_page_layout(self, name):
        try:
            return self._page_layout_registry[name.lower()]
        except KeyError:
            raise layout.LayoutDoesNotExist(name)
                

class WebSite(object):
    '''A class for callable objects used to load and configure a web site.
Users can subclass this class and override the :meth:`load` method or
the ``load_{{ name }}`` where ``name`` is the value of the
:attr:`name` attribute.
Instances are pickable so that they can be used to create site applications
in a multiprocessing framework. Typical usage::

    class Loader(djpcms.SiteLoader):
    
        def load(self):
            settings = djpcms.get_settings(__file__,
                                           APPLICATION_URLS = self.urls)
            return djpcms.Site(settings)
        
        def urls(self, site):
            return (
                Application('/',
                    name = 'Hello world example',
                    routes = (View(renderer = lambda request : 'Hello world!'),)
                ),)
 
The :meth:`load` or ``load_{{ name }}`` methods can have an attribute
**web_site** which if it does result in ``False`` will treat the loading not
for djpcms web sites.

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
    version = None
    _settings_file = None
    
    def __init__(self, name = None, **params):
        self.name = name
        self.local = {}
        self._settings_file = params.pop('settings_file', self._settings_file)
        self.callbacks = []
        params.pop('site',None)
        self.params = params
        
    def _set_settings_file(self, settings):
        self._settings_file = settings
        self.local.pop('site',None)
    def _get_settings_file(self):
        return self._settings_file
    settings_file = property(_get_settings_file,_set_settings_file)
    
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
            load = self.load
            if self.name:
                load = getattr(self,'load_{0}'.format(self.name))
            self.local['site'] = load()
            if self.site is not None:
                self.load_site()
                for callback in self.callbacks:
                    callback(self)
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
        '''Callback once the site is loaded.'''
        pass

    def wsgi(self):
        '''Return the WSGI handeler for your application.'''
        return http.WSGIhandler(self.wsgi_middleware(),
                                self.response_middleware())
    
    def load_site(self):
        self.site.load()