import os
from threading import Lock

from djpcms.core.exceptions import DjpcmsException, AlreadyRegistered,\
                                   ImproperlyConfigured, ApplicationNotAvailable
from djpcms.utils.collections import OrderedDict
from djpcms.utils.importer import import_module, module_attribute
from djpcms.core.urlresolvers import ResolverMixin

from djpcms.views import Application, ModelApplication, DummyDjp
from djpcms.template import loader

from djpcms.models import Page, InnerTemplate

from .handlers import WSGI


class ApplicationSite(ResolverMixin):
    '''Application site manager
    An instance of this class is used to handle url of
    registered applications.
    '''
    def __init__(self, root, url, config, handler):
        self.lock = Lock()
        self.root = root
        self.route = url
        self.url = url
        self.config = config
        self.settings = config
        self._registry = {}
        self._nameregistry = OrderedDict()
        self.choices = [('','-----------------')]
        self._request_middleware = None
        self._response_middleware = None
        self._template_context_processors = None
        #self.ModelApplication = ModelApplication
        handler = handler or WSGI
        self.handle = handler(self)
        
    def __repr__(self):
        return '{0} - {1}'.format(self.route,'loaded' if self.isloaded else 'not loaded')
    __str__ = __repr__
    
    def __get_User(self):
        return self.root.User
    def __set_User(self, User):
        if not self.root.User:
            self.root.User = User
        elif User is not self.root.User:
            raise ImproperlyConfigured('A different User class has been already registered')
    User = property(__get_User,__set_User)
    
    @property
    def tree(self):
        return self.root.tree
    
    def count(self):
        return len(self._registry)
    
    def __len__(self):
        return len(self._nameregistry)
    
    def __iter__(self):
        return self._nameregistry.__iter__()
        
    def _load(self):
        """Registers applications to the application site."""
        appurls = self.settings.APPLICATION_URLS
        if appurls:
            if not hasattr(appurls,'__call__'):
                if not hasattr(appurls,'__iter__'):
                    appurls = module_attribute(appurls,safe=False)
            if hasattr(appurls,'__call__'):
                appurls = appurls()
        # loop over reversed sorted applications
        if appurls:
            for application in reversed(sorted(appurls, key = lambda x : x.baseurl)):
                self.register(application)
        url = self.make_url
        urls = ()
        # Add in each model's views.
        applications = list(self._nameregistry.values())
        for app in applications:
            baseurl = app.baseurl
            if baseurl:
                urls += url('^{0}(.*)'.format(baseurl[1:]),
                            app,
                            name = app.name),
        node = self.tree.make_sitenode(self.route,self)
        node.addapplications(applications)
        return urls
        
    def register(self, application):
        if not isinstance(application,Application):
            raise DjpcmsException('Cannot register application. Is is not a valid one.')
        
        if application.name in self._nameregistry:
            raise AlreadyRegistered('Application %s already registered as application' % application)
        self._nameregistry[application.name] = application
        application.register(self)
        model = getattr(application,'model',None)
        if model:
            if model in self._registry:
                raise AlreadyRegistered('Model %s already registered as application' % model)
            self._registry[model] = application
        else:
            pass
    
    def unregister(self, model):
        '''Unregister the :class:`djpcms.views.ModelApplication` registered
for ``model``. Return the application class which has been unregistered.
If the ``model`` does not have an application it return ``None``.'''
        appmodel = self._registry.pop(model,None)
        if appmodel:
            self._nameregistry.pop(appmodel.name,None)
        return None if not appmodel else appmodel.__class__
    
    def clear(self):
        '''Clear the site from all applications'''
        ResolverMixin.clear(self)
        del self.choices[1:]
        self._nameregistry.clear()
        self._registry.clear()
            
    def for_model(self, model):
        '''Obtain a :class:`djpcms.views.appsite.ModelApplication` for model *model*.
If the application is not available, it returns ``None``. Never fails.'''
        #Allow for OrmWrapper
        if hasattr(model,'model'):
            model = model.model
        try:
            return self._registry.get(model,None)
        except:
            return None
            
    def getapp(self, appname):
        '''Given a *appname* in the form of appname-appview
returns the application handler. If the appname is not available, it raises a KeyError'''
        names = appname.split('-')
        if len(names) == 2:
            name     = names[0]
            app_code = names[1]
            appmodel = self._nameregistry.get(name,None)
            if appmodel:
                return appmodel.getview(app_code)
        appmodel = self._nameregistry.get(appname,None)
        if appmodel is None:
            raise ApplicationNotAvailable('Application {0} not available.'.format(appname))
        return appmodel.root_view
    
    def get_instanceurl(self, instance, view_name = 'view', **kwargs):
        '''Calculate a url given a instance'''
        app = self.for_model(instance.__class__)
        if app:
            view = app.getview(view_name)
            if view:
                try:
                    return view.get_url(None, instance = instance, **kwargs)
                except:
                    return None
        return None
    
    def get_url(self, model, view_name, instance = None, **kwargs):
        '''Build a url from a model, a view name and optionally a model instance'''
        if not isinstance(model,type):
            instance = model
            model = instance.__class__
        app = self.for_model(model)
        if app:
            view = app.getview(view_name)
            if view:
                try:
                    return view.get_url(DummyDjp(instance,kwargs))
                except:
                    return None
        return None
    
    def _load_middleware(self):
        if self._request_middleware is None:
            self._request_middleware = mw = []
            self._response_middleware = rw = []
            self._exception_middleware = ew = []
            self.lock.acquire()
            try:
                for middleware_path in self.settings.MIDDLEWARE_CLASSES:
                    mwcls = module_attribute(middleware_path,safe=True)
                    if mwcls:
                        mwobj = mwcls()
                        if hasattr(mwobj,'process_request'):
                            mw.append(mwobj.process_request)
                        if hasattr(mwobj,'process_response'):
                            rw.append(mwobj.process_response)
                        if hasattr(mwobj,'process_exception'):
                            ew.append(mwobj.process_exception)
            finally:
                self.lock.release()
                
    def _load_template_processors(self):
        if self._template_context_processors is None:
            self.lock.acquire()
            mw = []
            try:
                for p_path in self.settings.TEMPLATE_CONTEXT_PROCESSORS:
                    func = module_attribute(p_path,safe=True)
                    if func:
                        mw.append(func)
                self._template_context_processors = tuple(mw)
            finally:
                self.lock.release()
    
    def request_middleware(self):
        self._load_middleware()
        return self._request_middleware
    
    def response_middleware(self):
        self._load_middleware()
        return self._response_middleware
    
    def exception_middleware(self):
        self._load_middleware()
        return self._exception_middleware
    
    def template_context(self):
        self._load_template_processors()
        return self._template_context_processors
    
    @property
    def permissions(self):
        return self.root.permissions
    
    def add_default_inner_template(self, page):
        template_name = self.settings.DEFAULT_INNER_TEMPLATE
        if not template_name:
            return
        name = os.path.split(template_name)[1].split('.')[0]
        source, loc = loader.load_template_source(template_name)
        te = InnerTemplate(name = name, template = source)
        te.save()
        page.inner_template = te
        page.save()
        return te
    
    def resolve(self, path, subpath = None, site = None, numpass = 0):
        return super(ApplicationSite,self).resolve(path, subpath, site = self, numpass = numpass)
        
    def get_page(self, **kwargs):
        return Page.objects.get(**kwargs)
        
    def handle_exception(self, *args, **kwargs):
        return self.root.handle_exception(*args, **kwargs)
            
    