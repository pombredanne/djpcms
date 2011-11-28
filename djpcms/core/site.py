import os
import sys
import traceback
import logging
from copy import copy
from threading import Lock

from py2py3 import iteritems, itervalues

import djpcms
from djpcms.utils.conf import get_settings
from djpcms.utils.importer import import_module
from djpcms.utils import logtrace, closedurl, force_str
from djpcms.utils.dispatch import Signal

from .exceptions import AlreadyRegistered, PermissionDenied,\
                        ImproperlyConfigured, DjpcmsException,\
                        Http404
from .urlresolvers import ResolverMixin
from .management import find_commands
from .permissions import PermissionHandler
from . import http
from . import orms

__all__ = ['SiteLoader',
           'ApplicationSites',
           'ContextRenderer']


logger = logging.getLogger('djpcms')


class TreeUpdate(object):
    
    def __init__(self, sites):
        self.sites = sites
        if self.sites.Page:
            self.sites.Page.register_tree_update(self)
        
    def __call__(self, sender, instance = None, **kwargs):
        '''Register the page post save with tree'''
        if isinstance(instance, self.sites.Page):
            self.sites.tree.update_flat_pages()
            
            

class ContextRenderer(object):
    
    def __init__(self, djp, context = None, template = None, renderer = None,
                 text = None):
        self.djp = djp
        self.template = template
        self.context = context or {}
        self.renderer = renderer
        self._renderers = []
        if text is not None:
            self.text = text
        
    @classmethod
    def make(cls, txt):
        if isinstance(txt,cls):
            return txt
        else:
            return ContextRenderer(None,text = txt)
        
    @property
    def called(self):
        return hasattr(self,'text')
    
    def done(self):
        '''Return the text if already rendered otherwise return self'''
        if self.called:
            return self.text
        return self
    
    def render(self):
        if not self.called:
            self.text = text = self._render()
            renderers = self._renderers
            self._renderers = []
            for r in renderers:
                text = r(text)
            self.text = text
        return self.text
        
    def _render(self):
        if self.template:
            return self.djp.render_template(self.template,self.context)
        elif self.renderer:
            return self.renderer(self.djp,self.context)
        else:
            raise NotImplementedError
        
    def add_renderer(self, r):
        if hasattr(r,'__call__'):
            if self.called:
                self.text = r(self.text)
            else:
                self._renderers.append(r)


def default_response_handler(djp, response, callback = None):
    if isinstance(response,dict):
        rr = default_response_handler
        response = dict(((k,rr(djp,v)) for k,v in iteritems(response)))
    elif isinstance(response,ContextRenderer):
        response = response.render()
    return callback(response) if callback else response


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
            self.sites = ApplicationSites(self.route)
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

    def get_settings(self, name, settings = None, **params):
        '''
        Extra configuration parameters,
can be passed as key-value pairs:

:parameter name: file or directory name which specifies the
                 application root-directory.
                 
:parameter settings: optional settings file name specified as a dotted path
    relative ro the application directory.
    
    Default ``None``

:parameter params: key-value pairs which override the values
                   in the settings file.
'''
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
        
        return get_settings(settings_module_name,
                            SITE_DIRECTORY = site_path,
                            SITE_MODULE = name,
                            **params)
        
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
    
    
class ApplicationSites(ResolverMixin):
    '''Holder of application sites::

    import djpcms
    sites = djpcms.ApplicationSites()
    

:parameter route: optional base route for this site holder.
    Default: ``"/"``
    
:parameter response_handler: optional function for handling responses.


Attributes available:
    
.. attribute:: settings

    web site settings dictionary
    
.. attribute:: search_engine

    An instance of a search engine interface
    
.. attribute:: User

    The user model used by the site
    
'''
    profilig_key = None
    
    def __init__(self, route = '/', response_handler = None):
        super(ApplicationSites,self).__init__(route)
        self.internals['admins'] = []
        self.internals['response_handler'] = response_handler
        self.internals['permissions'] = PermissionHandler()
        self.internals['handle_exception'] = standard_exception_handle
        self.internals['on_site_loaded'] = Signal()
        self.internals['request_started'] = Signal()
        self.internals['start_response'] = Signal()
        self.internals['request_finished'] = Signal()
        
    def make_parent(self, parent):
        if parent is not None:
            raise ValueError('Cannot set parent')
    
    @property
    def ApplicationSite(self):
        from djpcms.views import ApplicationSite
        return ApplicationSite
    
    def all(self):
        return list(itervalues(self.routes))
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
        
    def setup_environment(self):
        '''Called just before loading
 :class:`djpcms.views.ApplicationSite` instances are registered.
It loops over the objecr relational mappers registered and setup models.
It also initialise admin for models.'''
        if not self:
            raise ImproperlyConfigured('Site container has no sites registered.\
 Cannot setup.')
        for wrapper in orms.model_wrappers.values():
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
        from .sitemap import SiteMap
        self.internals['tree'] = tree = SiteMap(self)
        self.setup_environment()
        urls = super(ApplicationSites,self)._load()
        self.on_site_loaded.send(self)
        self._tree_updated = TreeUpdate(self)
        return urls
    
    def make(self, settings, route = None, permissions = None):
        '''Create a new ``djpcms`` :class:`djpcms.views.ApplicationSite`.
    
:parameter route: the base ``url`` for the site applications.

    Default ``None``
    
:parameter permission: An optional :ref:`site permission handler <permissions>`.
:rtype: an instance of :class:`djpcms.views.ApplicationSite`.
'''
        # If no settings available get the current one
        if self.settings is None:
            self.internals['settings'] = settings
            sk = getattr(settings,'SECRET_KEY',None)
            if not sk:
                settings.SECRET_KEY = 'djpcms'
            os.environ['SECRET_KEY'] = settings.SECRET_KEY 
        
        # Add template media directory to template directories
        path = os.path.join(settings.SITE_DIRECTORY,'templates')
        if path not in settings.TEMPLATE_DIRS and os.path.isdir(path):
            settings.TEMPLATE_DIRS += path,
        path = os.path.join(djpcms.__path__[0],'media','djpcms')
        if path not in settings.TEMPLATE_DIRS:
            settings.TEMPLATE_DIRS += path,
        
        route = route or ''
        site = self.ApplicationSite(route, self, settings, permissions)
        if site.route.rule in self.routes:
            raise AlreadyRegistered('Site with route {0}\
 already avalable.'.format(route))
        self.routes[site.route.rule] = site
        self.__dict__.pop('_urls',None)
        return site
    
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
        
    def make_admin_urls(self, name = 'admin', **params):
        '''Return a one element tuple containing an
:class:`djpcms.apps.included.admin.AdminSite`
application for displaying the admin site. All application with an ``admin``
module specifying the admin application will be included.

:parameter params: key-value pairs of extra parameters for input in the
                   :class:`djpcms.apps.included.admin.AdminSite` constructor.'''
        from djpcms.apps.admin import AdminSite, ApplicationGroup
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
                    adming[rname] = route
                    agroups[route] = {'name':name_,
                                      'urls':urls}
#                    groups.append(ApplicationGroup(route,
#                                                   name = name_,
#                                                   apps = urls))
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
    

