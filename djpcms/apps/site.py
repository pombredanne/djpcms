import os
import sys
import traceback
import logging
from threading import Lock

import djpcms
from djpcms.conf import get_settings
from djpcms.core.exceptions import AlreadyRegistered, PermissionDenied,\
                                   ImproperlyConfigured, DjpcmsException,\
                                   Http404
from djpcms.utils.importer import import_module, import_modules
from djpcms.utils import logtrace, closedurl, force_str
from djpcms.utils.const import SLASH
from djpcms.utils.structures import OrderedDict
from djpcms.core.urlresolvers import ResolverMixin
from djpcms.dispatch import Signal

from .management import find_commands
from .permissions import PermissionHandler

__all__ = ['MakeSite',
           'SiteApp',
           'GetOrCreate',
           'RegisterORM',
           'ORMS',
           'adminurls',
           'get_site',
           'get_url',
           'get_urls',
           'loadapps',
           'sites']


logger = logging.getLogger('sites')

    
def standard_exception_handle(request, e, status = None):
    from djpcms import http
    from djpcms.template import loader
    status = status or getattr(e,'status',None) or 500
    info = request.DJPCMS
    site = info.site
    settings = site.settings
    exc_info = sys.exc_info()
    if site is None or not hasattr(site,'exception_middleware'):
        raise
    for middleware_method in site.exception_middleware():
        try:
            response = middleware_method(request, e, status)
            if response:
                return response
        except:
            exc_info = sys.exc_info()
    for middleware_method in site.request_middleware():
        try:
            response = middleware_method(request)
            if response:
                return response
        except:
            exc_info = sys.exc_info()
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
    ctx  = loader.context(ctx, request)
    html = loader.render((template,template2,template3,
                          'djpcms/errors/error.html'),
                         ctx)
    return http.Response(html.encode('latin-1','replace'),
                         status = status,
                         content_type = 'text/html',
                         encoding = settings.DEFAULT_CHARSET)
        

class SiteApp(ResolverMixin):
    
    def for_model(self, model):
        '''Obtain a :class:`djpcms.views.appsite.ModelApplication` for *model*.
If the application is not available, it returns ``None``. It never fails.'''
        return None
    
    def djp(self, request, path):
        '''Entry points for requests'''
        site,view,kwargs = self.resolve(path)
        return view(request, **kwargs)
    
    def _init(self):
        self.lock = Lock()
        self._search_engine = None
        
    @property
    def search_engine(self):
        if not self._search_engine and self.root is not self:
            return self.root.search_engine
        return self._search_engine
    
    @property
    def permissions(self):
        if not self._permissions and self.root is not self:
            return self.root.permissions
        else:
            return self._permissions
    
    

class ApplicationSites(SiteApp, djpcms.UnicodeMixin):
    '''This class is used as a singletone and holds information
of djpcms application routes as well as general configuration parameters.
When running a web site powered by djpcms, to access the sites signletone::

    from djpcms import sites


The sites singletone has several important attributes:

.. attribute:: root

    The site root. For the sites singletone this is ``None``
    
.. attribute:: settings

    web site settings dictionary
    
.. attribute:: search_engine

    An instance of a search engine interface
    
.. attribute:: User

    The user model used by the site
    
'''
    modelwrappers = OrderedDict()
    model_from_hash = {}
    profilig_key = None
    
    def __init__(self):
        self._init()
        self._permissions = PermissionHandler()
        self.handle_exception = standard_exception_handle
        self.on_site_loaded = Signal()
        self.request_started = Signal()
        self.start_response = Signal()
        self.request_finished = Signal()
        
    def _init(self):
        super(ApplicationSites,self)._init()
        self._sites = {}
        self.admins = []
        self._osites = None
        self.settings = None
        self.route = None
        self.tree = None
        self._commands = None
        self.User = None
        self.Page = None
        self.storage = None
        
    def clear(self):
        self._init()
        
    def __unicode__(self):
        return force_str(self._sites)
        
    def __len__(self):
        return len(self._sites)
    
    @property
    def ApplicationSite(self):
        from djpcms.views import ApplicationSite
        return ApplicationSite
    
    @property
    def root(self):
        return self
    
    def all(self):
        s = self._osites
        if s is None:
            self._osites = s = list(
                        OrderedDict(reversed(sorted(self._sites.items(),
                                           key=lambda x : x[0]))).values())
        return s                           
                                           
    def __iter__(self):
        return self.all().__iter__()
    
    def __getitem__(self, index):
        return self.all()[index]
    def __setitem(self, index, val):
        raise TypeError('Site object does not support item assignment')
    
    def setup_environment(self):
        '''Called just before loading
 :class:`djpcms.views.ApplicationSite` instances are registered.
It loops over the objecr relational mappers registered and setup models.
It also initialise admin for models.'''
        if not self:
            raise ImproperlyConfigured('Site container has no sites registered.\
 Cannot setup.')
        for wrapper in self.modelwrappers.values():
            wrapper.setup_environment(self)
        self.admins = admins = []
        for apps in self.settings.INSTALLED_APPS:
            if apps.startswith('django.'):
                continue
            try:
                mname = apps.split('.')[-1]
                admin = import_module('{0}.admin'.format(apps))
                urls  = getattr(admin,'admin_urls',None)
                if not urls:
                    continue
                name = getattr(admin,'NAME',mname)
                route  = closedurl(getattr(admin,'ROUTE',mname))
                admins.append((name,route,urls))
            except ImportError:
                continue            
        
    def _load(self):
        '''Load sites and flat pages'''
        from djpcms.views import SiteMap, ALL_URLS
        if not self._sites:
            raise ImproperlyConfigured('No sites registered.')
        # setup the environment
        self.setup_environment()
        settings = self.settings
        sites = self.all()
        if sites[-1].path is not SLASH:
            raise ImproperlyConfigured('There must be a root site available.')
        self.tree = tree = SiteMap(self)
        for site in reversed(sites):
            site.load()
        import_modules(settings.DJPCMS_PLUGINS)
        import_modules(settings.DJPCMS_WRAPPERS)
        url = self.make_url
        urls = ()
        for site in sites:
            regex = site.route() + ALL_URLS
            urls += url(str(regex), site),
        # Load flat pages to site map
        self.tree.load()
        self.on_site_loaded.send(self)
        return urls
    
    def make(self, name, settings = None, route = None,
             permissions = None, **params):
        '''Create a new ``djpcms`` :class:`djpcms.views.ApplicationSite`
from a directory or a file *name*. Extra configuration parameters,
can be passed as key-value pairs:

:parameter name: file or directory name which specifies the
                 application root-directory.
                 
:parameter settings: optional settings file name specified as a dotted path
    relative ro the application directory.
    
    Default ``None``
    
:parameter route: the base ``url`` for the site applications.

    Default ``None``
    
:parameter permission: An optional :ref:`site permission handler <permissions>`.
:parameter params: key-value pairs which override the values
                   in the settings file.

The function returns an instance of
:class:`djpcms.views.ApplicationSite`.
'''
        # Finde directory from name. If not a directory it may be a file
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
        
        settings = get_settings(settings_module_name,
                                SITE_DIRECTORY = site_path,
                                SITE_MODULE = name,
                                **params)
        
        # If no settings available get the current one
        if self.settings is None:
            self.settings = settings
            sk = getattr(settings,'SECRET_KEY',None)
            if not sk:
                settings.SECRET_KEY = 'djpcms'
            os.environ['SECRET_KEY'] = settings.SECRET_KEY 
        
        # Add template media directory to template directories
        path = os.path.join(site_path,'templates')
        if path not in settings.TEMPLATE_DIRS and os.path.isdir(path):
            settings.TEMPLATE_DIRS += path,
        path = os.path.join(djpcms.__path__[0],'media','djpcms')
        if path not in settings.TEMPLATE_DIRS:
            settings.TEMPLATE_DIRS += path,
        
        return self._create_site(route,settings,permissions)
    
    def loadsettings(self, setting_module):
        '''Load settings to override existing settings'''
        if not self:
            raise ValueError('Cannot load settings. No site installed')
        setting_module = '{0}.{1}'.format(self.settings.SITE_MODULE,
                                          setting_module)
        setting_module = import_module(setting_module)
        self.settings.fill(setting_module)
        
    def get_or_create(self, name, settings = None,
                      route = None, **params):
        '''Same as :meth:`make` but does nothing if an application
site is already registered at ``route``.'''
        route = closedurl(route or '')
        site = self.get(route,None)
        if site is None:
            return self.make(name,settings,route,**params)
        else:
            return site
    
    def _create_site(self,route,settings,permissions):
        route = closedurl(route or '')
        if route in self._sites:
            raise AlreadyRegistered('Site with route {0}\
 already avalable.'.format(route))
        site = self.ApplicationSite(self, route, settings, permissions)
        self._sites[site.path] = site
        self._osites = None
        self._urls = None
        return site
    
    def get(self, name, default = None):
        return self._sites.get(name,default)
            
    def get_site(self, url = None):
        url = url or SLASH
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
        
    def make_admin_urls(self, name = 'admin', **params):
        '''Return a one element tuple containing an
:class:`djpcms.apps.included.admin.AdminSite`
application for displaying the admin site. All application with an ``admin``
module specifying the admin application will be included.

:parameter params: key-value pairs of extra parameters for input in the
                   :class:`djpcms.apps.included.admin.AdminSite` constructor.'''
        from djpcms.apps.included.admin import AdminSite, ApplicationGroup
        adming = {}
        agroups = {}
        if self.settings.ADMIN_GROUPING:
            for url,v in self.settings.ADMIN_GROUPING.items():
                for app in v['apps']:
                    if app not in adming:
                        adming[app] = url
                        if url not in agroups:
                            v = v.copy()
                            v['urls'] = ()
                            agroups[url] = v
        groups = []
        for name_,route,urls in self.admins:
            if urls:
                rname = route[1:-1]
                if rname in adming:
                    url = adming[rname]
                    agroups[url]['urls'] += urls
                else:
                    groups.append(ApplicationGroup(route,
                                                   name = name_,
                                                   apps = urls))
        for route,data in agroups.items():
            groups.append(ApplicationGroup(route,
                                           name = data['name'],
                                           apps = data['urls']))
            
        # Create the admin application
        admin = AdminSite('/', apps = groups, name = name, **params)
        return (admin,)
    
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
                    command_module = 'djpcms.apps'
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
    
    
           
        
sites = ApplicationSites()

model_wrappers = sites.modelwrappers
MakeSite = sites.make
adminurls = sites.make_admin_urls
GetOrCreate = sites.get_or_create
get_site = sites.get_site
get_url  = sites.get_url
get_urls = sites.get_urls
loadapps = sites.load

ORMS = lambda : model_wrappers.values()

def RegisterORM(name):
    '''Register a new Object Relational Mapper to Djpcms. ``name`` is the
dotted path to a python module containing a class named ``OrmWrapper``
derived from :class:`BaseOrmWrapper`.'''
    global model_wrappers
    names = name.split('.')
    if len(names) == 1:
        mod_name = 'djpcms.core.orms._' + name
    else:
        mod_name = name
    try:
        mod = import_module(mod_name)
    except ImportError as e:
        return
    model_wrappers[name] = mod.OrmWrapper

