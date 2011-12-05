import os
import sys
import logging
from inspect import isclass
from copy import copy, deepcopy

from py2py3 import iteritems, itervalues, native_str

import djpcms
from djpcms import html
from djpcms.utils.importer import import_module, module_attribute
from djpcms.utils import conf, force_str, lazyproperty

from .exceptions import AlreadyRegistered, PermissionDenied,\
                        ImproperlyConfigured, DjpcmsException,\
                        Http404
from .urlresolvers import ResolverMixin
from .management import find_commands
from .permissions import PermissionHandler, SimpleRobots
from .cache import CacheHandler
from .async import default_response_handler
from . import http
from . import orms


__all__ = ['Site', 'get_settings']


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
    
    return conf.Config(settings_module_name,
                       SITE_DIRECTORY = site_path,
                       SITE_MODULE = name,
                       **params)


def default_layout(request, context):
    return request.view.template.render(request.template_file,
                                        context,
                                        request = request,
                                        encode = 'latin-1',
                                        encode_errors = 'replace')
    
    
DEFAULT_SITE_HANDLERS = {
    'response_handler': default_response_handler,
    'permissions': PermissionHandler,
    'meta_robots': SimpleRobots,
    'errors': http.standard_exception_handle,
    'page_layout': default_layout,
    'cache': CacheHandler()
}


def add_default_handlers(site):
    internals = site.internals
    for key,value in DEFAULT_SITE_HANDLERS.items():
        if key not in internals:
            if isclass(value):
                value = value()
            internals[key] = value
        
        
class Site(ResolverMixin,html.Renderer):
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
        super(Site,self).__init__(route,parent)
        self._model_registry = {}
        self.plugin_choices = [('','-----------------')]
        if self.parent is None:
            settings = settings or get_settings()
        path = os.path.join(settings.SITE_DIRECTORY,'templates')
        if path not in settings.TEMPLATE_DIRS and os.path.isdir(path):
            settings.TEMPLATE_DIRS += path,
        path = os.path.join(djpcms.__path__[0],'media','djpcms')
        if path not in settings.TEMPLATE_DIRS:
            settings.TEMPLATE_DIRS += path,
        if settings:
            self.internals['settings'] = settings
        self.internals.update(handlers)
        
    def _load(self):
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
                appurls = appurls()
            self.routes.extend(appurls)
            
        self.internals['template'] = html.ContextTemplate(self)
        return super(Site,self)._load()
    
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
    
        
    # TO BE CHECKED
    
    
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
    
    def setsettings(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self.settings,k,v)
            for site in self:
                setattr(site.settings,k,v)
            
    def registered_models(self):
        '''Generator of model Choices'''
        p = set()
        for site in self.all():
            for model in site._registry:
                if model not in p:
                    p.add(model)
                    yield model
    