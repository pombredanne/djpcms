import os
import sys
import logging
from inspect import isclass
from copy import copy

from pulsar import coroutine_return
from pulsar.utils.path import Path
from pulsar.utils.log import local_method
from pulsar.utils.structures import OrderedDict
from pulsar.utils.importer import (import_module, module_attribute,
                                   import_modules)
from pulsar.apps.wsgi import LazyWsgi, WsgiHandler, WsgiResponse
from pulsar.utils.log import lazyproperty

from djpcms import is_renderer, ajax
from djpcms.utils import orms
from djpcms.html import layout, Widget, error_title, classes, html_trace
from djpcms.utils.httpurl import (iteritems, itervalues, native_str,
                                  iri_to_uri, REDIRECT_CODES)

from .conf import Config
from .exceptions import *
from .urlresolvers import ResolverMixin
from .management import find_commands
from .permissions import PermissionHandler, SimpleRobots
from .cache import CacheHandler
from .views import ViewRenderer
from .submit import SubmitDataMiddleware
from .request import get_request
from .tree import DjpcmsTree, BadNode


__all__ = ['Site', 'get_settings', 'WebSite', 'request_processor']


def get_settings(name=None, settings=None, **params):
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
                settings_module_name = '{0}.{1}'.format(name, settings)
            else:
                settings_module_name = settings
    else:
        settings_module_name = None
    return Config(settings_module_name,
                  SITE_DIRECTORY=site_path,
                  SITE_MODULE=name,
                  **params)


DEFAULT_SITE_HANDLERS = {
    'meta_robots': SimpleRobots,
    'cache': CacheHandler()
}


def add_default_handlers(site):
    internals = site.internals
    for key, value in DEFAULT_SITE_HANDLERS.items():
        handler = internals.get(key)
        if handler is None:
            if isclass(value):
                value = value(site.settings)
            internals[key] = value

def request_processor(f):
    f.request_processor = True
    return f


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

.. hidden_data_middleware::

    A list of callables used to fill a data dictionary to include in forms
    as hidden fields.

'''
    logger = None

    def __init__(self, settings=None, route='/', parent=None,
                 routes=None, APPLICATION_URLS=None, **handlers):
        super(Site, self).__init__(route, routes=routes)
        self.APPLICATION_URLS = APPLICATION_URLS
        self._model_registry = {}
        self._page_layout_registry = OrderedDict()
        self.plugin_choices = [('','-----------------')]
        self.request_processors = []
        if parent is None:
            self.submit_data_middleware = SubmitDataMiddleware()
            settings = settings or get_settings()
            if not handlers.get('permissions'):
                handlers['permissions'] = PermissionHandler(settings)
        else:
            self.submit_data_middleware = parent.submit_data_middleware
            self.parent = parent
        if settings:
            self.internals['settings'] = settings
        self.internals.update(handlers)
        self.register_page_layout('default')
        self.logger = logging.getLogger('djpcms')

    def setup_environment(self):
        '''Set up the the site.'''
        for app in self.settings.INSTALLED_APPS:
            try:
                mod = import_module(app+'.request')
                for name in dir(mod):
                    processor = getattr(mod, name)
                    if getattr(processor, 'request_processor', False):
                        self.request_processors.append(processor)
            except ImportError as e:
                pass
        if self.root == self:
            for wrapper in orms.model_wrappers.values():
                wrapper.setup_environment(self)
            add_default_handlers(self)
        appurls = self.APPLICATION_URLS
        if appurls:
            if not hasattr(appurls, '__call__'):
                if isinstance(appurls, str):
                    appurls = module_attribute(appurls,safe=False)
            if hasattr(appurls,'__call__'):
                appurls = appurls(self)
            self.routes.extend(copy(appurls))
        return len(self)

    def _load(self):
        self.setup_environment()
        urls = super(Site, self)._load()
        import_modules(self.settings.DJPCMS_PLUGINS)
        import_modules(self.settings.DJPCMS_WRAPPERS)
        return urls

    def _site(self):
        return self

    def addsite(self, settings=None, route=None, APPLICATION_URLS=None,
                **handlers):
        '''Add a new :class:`Site` to ``self``.

:parameter settings: Optional settings for the site.
:parameter route: the base ``url`` for the site.
:parameter permission: An optional :ref:`site permission handler <permissions>`.
:rtype: an instance of :class:`Site`.
'''
        if self.isbound:
            raise ValueError('Cannot add a new site.')
        site = Site(settings=settings,
                    route=route or '',
                    parent=self,
                    APPLICATION_URLS=APPLICATION_URLS,
                    **handlers)
        self.routes.append(site)
        return site

    def for_model(self, model, all=False, start=True):
        '''Obtain a :class:`Application` for model *model*.
If the application is not available, it returns ``None``. It never fails.
If *all* is set to ``True`` it returns a list of all the :class:`Application`
for that model.'''
        if not model:
            return
        if hasattr(model, 'model'):
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
                command_module = app_name
                if app_name == 'djpcms':
                    command_module = 'djpcms.cms'
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

    def register_page_layout(self, name, page=None):
        '''Register a :class:`djpcms.html.layout.page` with the
:class:`Site`. Return self for concatenating calls.'''
        name = name.lower()
        if page is None:
            page = layout.page()
        self._page_layout_registry[name] = page
        return self

    def get_page_layout(self, *names):
        for name in names:
            try:
                return self._page_layout_registry[name.lower()]
            except KeyError:
                continue
        raise layout.LayoutDoesNotExist(', '.join(names))

    def __call__(self, environ, start_response):
        try:
            page = self.models.page
        except AttributeError:
            tree = DjpcmsTree(self.tree)
        else:
            pages = yield page.query().all()
            tree = DjpcmsTree(self.tree, pages)
        node = tree.resolve(environ['PATH_INFO'])
        request = get_request(environ, node=node)
        content = request.view(request)
        if isinstance(content, WsgiResponse):
            response = content
        else:
            response = yield content.http_response(request)
        coroutine_return(response)


class WebSite(LazyWsgi):
    '''The lazy Wsgi handler.
Users can subclass this class and override the :meth:`setup` method or
the ``load_{{ name }}`` where ``name`` is the value of the
:attr:`name` attribute.
Instances are pickable so that they can be used to create site applications
in a multiprocessing framework. Typical usage::

    class Loader(djpcms.SiteLoader):

        def load(self):
            settings = djpcms.get_settings(__file__)
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
    settings_file = None

    def setup(self, environ=None):
        '''create the :class:`Site` for your web.

        :rtype: an instance of :class:`Site`.
        '''
        return WsgiHandler(self.site())

    @local_method
    def site(self):
        site = self._create_site()
        site.load()
        return site

    def on_pulsar_app_ready(self, app):
        pass

    def _create_site(self):
        settings = get_settings(settings=self.settings)
        return Site(settings)
