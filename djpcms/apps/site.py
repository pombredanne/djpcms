import os
import sys
import traceback
import logging

import djpcms
from djpcms.conf import get_settings
from djpcms.core.exceptions import AlreadyRegistered, PermissionDenied,\
                                   ImproperlyConfigured, DjpcmsException
from djpcms.utils.importer import import_module, import_modules
from djpcms.utils import logtrace, closedurl
from djpcms.utils.const import SLASH
from djpcms.utils.collections import OrderedDict
from djpcms.core.urlresolvers import ResolverMixin


__all__ = ['MakeSite',
           'GetOrCreate',
           'RegisterORM',
           'adminurls',
           'get_site',
           'get_url',
           'get_urls',
           'loadapps',
           'sites',
           'VIEW',
           'ADD',
           'CHANGE',
           'DELETE']


# Main permission flags
VIEW = 10
ADD = 20
CHANGE = 30
DELETE = 40


logger = logging.getLogger('sites')


def make_site(self, route, *args):
    from djpcms.apps import appsites
    return appsites.ApplicationSite(self, route, *args)
    
    
class SimplePermissionBackend(object):
    
    def has(self, request, permission_code, obj, user = None):
        if permission_code <= VIEW:
            return True
        else:
            return request.user.is_superuser
        
        
def standard_exception_handle(request, e, status = None):
    from djpcms.template import loader
    status = status or getattr(e,'status',None) or 500
    info = request.DJPCMS
    site = info.site
    if not site or not hasattr(site,'exception_middleware'):
        raise
    for middleware_method in site.exception_middleware():
        response = middleware_method(request, e, status)
        if response:
            return response
    for middleware_method in site.request_middleware():
        response = middleware_method(request)
        if response:
            return response
    exc_info = sys.exc_info()
    template = '{0}.html'.format(status)
    logtrace(logger, request, exc_info, status)
    stack_trace = '<p>{0}</p>'.format('</p>\n<p>'.join(traceback.format_exception(*exc_info)))
    ctx  = loader.context({'status':status,
                           'stack_trace':stack_trace,
                           'request':request,
                           'settings':site.settings},request)
    html = loader.render((template,
                          'djpcms/errors/'+template,
                          'djpcms/errors/error.html'),
                         ctx)
    return site.http.HttpResponse(html,
                                  status = status,
                                  mimetype = 'text/html')
        

class SiteMixin(ResolverMixin):
    
    def for_model(self, model):
        '''Obtain a :class:`djpcms.views.appsite.ModelApplication` for *model*.
If the application is not available, it returns ``None``. It never fails.'''
        return None
    
    def djp(self, request, path):
        '''Entry points for requests'''
        site,view,kwargs = self.resolve(path)
        return view(request, **kwargs)
    

class ApplicationSites(SiteMixin):
    '''This class is used as a singletone and holds information
of djpcms application routes as well as general configuration parameters.'''
    modelwrappers = {}
    
    def __init__(self):
        self._sites = {}
        self.clear()
        self.permissions = SimplePermissionBackend()
        self.handle_exception = standard_exception_handle
        
    def clear(self):
        self._sites.clear()
        self.admins = []
        self._osites = None
        self._settings = None
        self._default_settings = None
        self.route = None
        self.tree = None
        self.model_from_hash = {}
        self.User = None
        ResolverMixin.clear(self)
        for wrapper in self.modelwrappers.values():
            wrapper.clear()
        
    def register_orm(self, name):
        '''Register a new Object Relational Mapper to Djpcms. ``name`` is the
    dotted path to a python module containing a class named ``OrmWrapper``
    derived from :class:`BaseOrmWrapper`.'''
        names = name.split('.')
        if len(names) == 1:
            mod_name = 'djpcms.core.orms._' + name
        else:
            mod_name = name
        try:
            mod = import_module(mod_name)
        except ImportError:
            return
        self.modelwrappers[name] = mod.OrmWrapper
        
    def __len__(self):
        return len(self._sites)
    
    def all(self):
        s = self._osites
        if s is None:
            self._osites = s = list(OrderedDict(reversed(sorted(self._sites.items(),
                                           key=lambda x : x[0]))).values())
        return s                           
                                           
    def __iter__(self):
        return self.all().__iter__()
    
    def __getitem__(self, index):
        return self.all()[index]
    def __setitem(self, index, val):
        raise TypeError('Site object does not support item assignment')
        
    def __get_settings(self):
        if not self._settings:
            if not self._default_settings:
                self._default_settings = get_settings()
            return self._default_settings
        else:
            return self._settings
    settings = property(__get_settings)
    
    def setup_environment(self):
        '''Called just before loading :class:`djpcms.apps.appsites.ApplicationSite` instances
registered. It loops over the objecr relational mappers registered and setup models.
It also initialise admin for models.'''
        for wrapper in self.modelwrappers.values():
            wrapper.setup_environment(self)
        self.admins = admins = []
        for apps in self.settings.INSTALLED_APPS:
            try:
                mname = apps.split('.')[-1]
                admin = import_module(apps+'.admin')
                urls  = getattr(admin,'admin_urls',None)
                if not urls:
                    continue
                name = getattr(admin,'NAME',mname)
                route  = closedurl(getattr(admin,'ROUTE',mname))
                admins.append((name,route,urls))
            except ImportError:
                continue            
        
    def _load(self):
        '''Load sites'''
        from djpcms.views import SiteMap
        if not self._sites:
            raise ImproperlyConfigured('No sites registered.')
        # setup the environment
        self.setup_environment()
        settings = self.settings
        sites = self.all()
        if sites[-1].route is not SLASH:
            raise ImproperlyConfigured('There must be a root site available.')
        self.tree = tree = SiteMap()
        for site in reversed(sites):
            site.load()
        import_modules(settings.DJPCMS_PLUGINS)
        import_modules(settings.DJPCMS_WRAPPERS)
        url = self.make_url
        urls = ()
        for site in sites:
            urls += url(r'^{0}(.*)'.format(site.route[1:]), site),
        return urls
    
    def make(self, name, settings = None, route = None,
             handler = None, clearlog = True, 
             **params):
        '''Create a new ``djpcms`` :class:`djpcms.apps.appsites.ApplicationSite`
from a directory or a file name. Extra configuration parameters,
can be passed as key-value pairs:

:parameter name: a file or directory name where which specifies the application root-directory.
:parameter settings: optional settings file name.
:parameter route: the base ``url`` for the site applications.
:parameter handler: an optional string defining the wsgi handler class for the application.
:parameter params: key-value pairs which override the values in the settings file.

The function returns an instance of
:class:`djpcms.apps.appsites.ApplicationSite`.
'''

        # if not a directory it may be a file
        if os.path.isdir(name):
            appdir = name
        elif os.path.isfile(name):
            appdir = os.path.split(os.path.realpath(name))[0]
        else:
            try:
                mod = import_module(name)
                appdir = mod.__path__[0]
            except ImportError:
                raise ValueError('Could not find directory or file {0}'.format(name))
        path = os.path.realpath(appdir)
        base,name = os.path.split(path)
        if base not in sys.path:
            sys.path.insert(0, base)
        
        # Import settings
        settings = settings or 'settings'
        if '.' in settings:
            settings_module_name = settings
        else:
            sett = '{0}.py'.format(os.path.join(path,settings))
            if os.path.isfile(sett):
                settings_module_name = '{0}.{1}'.format(name,settings)
            else:
                settings_module_name = None
        
        settings = get_settings(settings_module_name,
                                SITE_DIRECTORY = path,
                                SITE_MODULE = name,
                                **params)
        
        # If no settings available get the current one
        if self._settings is None:
            self._settings = settings
            sk = getattr(settings,'SECRET_KEY',None)
            if not sk:
                settings.SECRET_KEY = 'djpcms'
            djpcms.init_logging(clearlog)
        
        # Add template media directory to template directories
        path = os.path.join(djpcms.__path__[0],'media','djpcms')
        if path not in settings.TEMPLATE_DIRS:
            settings.TEMPLATE_DIRS += path,
        
        self.logger = logging.getLogger('ApplicationSites')
        
        return self._create_site(route,settings,handler)
    
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
    
    def _create_site(self,route,settings,handler):
        from djpcms.apps import appsites
        route = closedurl(route or '')
        self.logger.debug('Creating new site at route "{0}"'.format(route))
        if route in self._sites:
            raise AlreadyRegistered('Site with route {0} already avalable.'.format(route))
        site = appsites.ApplicationSite(self, route, settings, handler)
        self._sites[site.route] = site
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
            except self.http.Http404:
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
        '''Return a one element tuple containing an :class:`djpcms.apps.included.admin.AdminSite`
application for displaying the admin site. All application with an ``admin`` module specifying the
admin application will be included.

:parameter params: key-value pairs of extra parameters for input in the
                   :class:`djpcms.apps.included.admin.AdminSite` constructor.'''
        from djpcms.apps.included.admin import AdminSite, ApplicationGroup
        groups = []
        for name_,route,urls in self.admins:
            if urls:
                groups.append(ApplicationGroup(route,
                                               name = name_,
                                               apps = urls))
        # Create the admin application
        admin = AdminSite('/', apps = groups, name = name, **params)
        return (admin,)
    
    def for_model(self, model):
        if not model:
            return
        r = None
        for site in self.all():
            r2 = site.for_model(model)
            if r2:
                if r:
                    raise DjpcmsException('Model {0} is registered with \
more than one site. Cannot resolve.'.format(model))
                r = r2
        return r            
        
sites = ApplicationSites()

MakeSite = sites.make
RegisterORM = sites.register_orm
adminurls = sites.make_admin_urls
GetOrCreate = sites.get_or_create
get_site = sites.get_site
get_url  = sites.get_url
get_urls = sites.get_urls
loadapps = sites.load

