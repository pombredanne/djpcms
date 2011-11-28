import os
from copy import deepcopy
from inspect import isclass

from py2py3 import is_bytes_or_string

from djpcms import http, ResolverMixin, html
from djpcms.core.exceptions import DjpcmsException, AlreadyRegistered,\
                                   ImproperlyConfigured,\
                                   ApplicationNotAvailable
from djpcms.utils.structures import OrderedDict
from djpcms.utils.importer import import_module, module_attribute
from djpcms.core.orms import mapper, model_from_hash
from djpcms.views import Application, DummyDjp


__all__ = ['ApplicationSite']


class ApplicationSite(ResolverMixin):
    '''A :class:`djpcms.ResolverMixin` for managing
:class:`Application` instances and other :class:`ApplicationSite`
registered with it.
'''
    def __init__(self, route, parent, config, permissions):
        super(ApplicationSite,self).__init__(route, parent)
        self.internals['settings'] = config
        self.internals['permissions'] = permissions
        self._model_registry = {}
        self._name_registry = {}
        self.choices = [('','-----------------')]
        self._template_context_processors = None
        
    def _load(self):
        """Registers applications to the application site."""
        appurls = self.settings.APPLICATION_URLS
        if appurls:
            if not hasattr(appurls,'__call__'):
                if is_bytes_or_string(appurls):
                    appurls = module_attribute(appurls,safe=False)
            if hasattr(appurls,'__call__'):
                appurls = appurls()
            self.routes.update(((a.rel_route,self._register(a)) for a in appurls))
        #self.tree.addsite(self)
        self.template = html.ContextTemplate(self)
        return super(ApplicationSite,self)._load()
    
    def _register(self, application, parent = None):
        if not isinstance(application,Application):
            raise DjpcmsException('Cannot register application.\
 Is is not a valid one.')
        apps = application.apps
        application.apps = None
        registered_application = deepcopy(application)
        application.apps = apps
        if registered_application.name in self._name_registry:
            raise AlreadyRegistered('Application with name "{0}"\
 already registered with site "{1}". {2}'
.format(application.name,self.path,self._name_registry[application.name]))
        model = registered_application.model
        if model:
            if model in self._model_registry:
                raise AlreadyRegistered('Model %s already registered\
 as application' % model)
            self._model_registry[model] = registered_application
            
        # Handle parent application if available
        if parent:
            parent_view = registered_application.parent
            if not parent_view:
                parent_view = parent.root_view
            elif parent_view not in parent.views:
                raise ApplicationUrlException("Parent {0} not available\
 in views.".format(parent))
            else:
                parent_view = parent.views[parent_view]
            registered_application.parent = parent_view
            registered_application.baseurl = parent_view.baseurl +\
                                             parent_view.regex + \
                                             registered_application.baseurl 
            
        # Create application views
        registered_application._create_views(self)
        self._name_registry[registered_application.name] =\
                                                     registered_application
        urls = []
        for view in registered_application.views.values():
            view_name  = registered_application._get_view_name(view.name)
            nurl = registered_application.make_url(regex = str(view.regex),
                                                   view  = view,
                                                   name  = view_name)
            urls.append(nurl)
        registered_application._urls = tuple(urls)
        
        napps = OrderedDict()
        for app in apps.values():
            app = self._register(app, parent = registered_application)
            napps[app.name] = app
        
        registered_application.apps = napps
        registered_application.registration_done()
        
        return registered_application
            
    def for_model(self, model, all = False):
        '''Obtain a :class:`Application` for model *model*.
If the application is not available, it returns ``None``. Never fails.'''
        #Allow for OrmWrapper
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
    
    def getapp(self, appname):
        '''Given a *appname* in the form of appname-appview
returns the application handler. If the appname is not available,
it raises a KeyError'''
        names = appname.split('-')
        if len(names) == 2:
            name     = names[0]
            app_code = names[1]
            appmodel = self._name_registry.get(name,None)
            if appmodel:
                return appmodel.getview(app_code)
        appmodel = self._name_registry.get(appname,None)
        if appmodel is None:
            raise ApplicationNotAvailable('Application {0}\
 not available.'.format(appname))
        return appmodel.root_view
    
    def get_instanceurl(self, instance, view_name = 'view', **kwargs):
        '''Calculate a url given a instance'''
        #TODO REMOVE IT
        app = self.for_model(instance.__class__)
        if app:
            view = app.getview(view_name)
            if view:
                try:
                    return view.get_url(None, instance = instance, **kwargs)
                except:
                    return None
        return None
    
    def get_url(self, model_or_instance, view_name = None, request = None,
                all = False, **kwargs):
        '''Build a url from a *model_or_instance* input and an
optional view name.

:parameter model_or_instance: a model or an instance of a model.
:parameter view_name: an optional view name. If not defined the view_name will
                be "search" if `model_or_instance` is a model, otherwise
                "view" if it is an instance of a model.
                
This method is safe and return None if no url is found.
'''
        if isclass(model_or_instance):
            model = model_or_instance
            instance = None
            view_name = view_name or 'search'
        else:
            instance = model_or_instance
            model = model_or_instance.__class__
            view_name = view_name or 'view'
            
        app = self.for_model(model, all = all)
        if app:
            view = app.getview(view_name)
            if view:
                try:
                    if request:
                        return view(request, instance = instance).url
                    else:
                        return view.get_url(DummyDjp(instance,kwargs))
                except:
                    return None
        return None
                
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
    
    def template_context(self):
        self._load_template_processors()
        return self._template_context_processors
    
    def add_default_inner_template(self, page):
        from djpcms.models import InnerTemplate
        template_name = self.settings.DEFAULT_INNER_TEMPLATE
        if not template_name:
            return
        name = os.path.split(template_name)[1].split('.')[0]
        mp = mapper(InnerTemplate)
        try:
            te = mp.get(name = name)
        except mp.DoesNotExist:
            source, loc = self.template.load_template_source(template_name)
            te = InnerTemplate(name = name, template = source)
            te.save()
        page.inner_template = te
        page.save()
        return te
    
    def resolve(self, path):
        return self.root.resolve(path)
        
    def get_page(self, **kwargs):
        from djpcms.models import Page
        return Page.objects.get(**kwargs)
        
    def handle_exception(self, *args, **kwargs):
        return self.root.handle_exception(*args, **kwargs)
            
    