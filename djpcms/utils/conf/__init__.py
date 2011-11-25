import os

from py2py3 import is_bytes_or_string

from djpcms.utils.importer import import_module

from . import defaults


class get_settings(object):
    django_settings = None
    
    def __init__(self, settings_module_name, **kwargs):
        self.__dict__['_values'] = {}
        self.__dict__['_settings'] = []
        self.__dict__['settings_module_name'] = settings_module_name
        self.fill(defaults)
        path = ''
        if self.settings_module_name:
            settings_module = import_module(settings_module_name)
            path = settings_module.__file__
            if path.endswith('.pyc'):
                path = path[:-1]
            self.fill(settings_module)
        self.__dict__['path'] = path
        self.update(kwargs)
        de = self.DEFAULT_TEMPLATE_NAME
        if de:
            if is_bytes_or_string(de):
                de = (de,)
            else:
                de = tuple(de)
        else:
            de = ()
        self.DEFAULT_TEMPLATE_NAME = de
        self.application_settings()
        
    def __repr__(self):
        return self._values.__repr__()
    __str__  = __repr__
    
    def update(self, mapping):
        v = self._values
        for sett,val in mapping.items():
            if sett == sett.upper():
                v[sett] = val
   
    def fill(self, mod, override = True):
        v = self._values
        for sett in dir(mod):
            setts = sett.split('__')
            s = setts[0]
            if s == s.upper():
                d = v
                for s in setts[:-1]:
                    if s not in d:
                        d[s] = {}
                    d = d[s]
                s = setts[-1]
                if s not in d or override:
                    d[s] = getattr(mod, sett)
                    
    def has(self, name):
        return name in self._settings
    
    def addsetting(self, setting):
        self._settings.append(setting)
        self.fill(setting,False)
        for sett,value in self._values.items():
            setattr(setting,sett,value)
        
    def get(self, name, default = None):
        try:
            return getattr(self,name)
        except AttributeError:
            return default
       
    def __contains__(self, name):
        return name in self._values
    
    def __getitem__(self, name):
        return self._values[name]
    
    def __getattr__(self, name):
        try:
            return self._values[name]
        except KeyError:
            raise AttributeError('Attribute {0} not available'.format(name))
    
    def __setattr__(self, name, value):
        self._values[name] = value
        for sett in self._settings:
            setattr(sett,name,value)
    
    def application_settings(self):
        for app in self.INSTALLED_APPS:
            if app == 'djpcms':
                continue
            name = '{0}.conf'.format(app)
            try:
                mod = import_module(name)
            except ImportError:
                continue
            self.fill(mod, override = False)
            
    def setup_django(self):
        '''Set up django if needed'''
        if self.__class__.django_settings:
            return
        if self.CMS_ORM == 'django' or self.TEMPLATE_ENGINE == 'django' or \
            self.DJANGO:
            ENVIRONMENT_VARIABLE = "DJANGO_SETTINGS_MODULE"
            settings_file = os.environ.get(ENVIRONMENT_VARIABLE,None)
            if not settings_file:
                settings_file = 'djpcms.apps.djangosite.settings'
            os.environ[ENVIRONMENT_VARIABLE] = settings_file
            
            from django.conf import settings as framework_settings
            self.addsetting(framework_settings)
            self.DJANGO = True
            self.__class__.django_settings = framework_settings
        return self.__class__.django_settings
        
