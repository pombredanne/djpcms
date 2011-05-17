import os

from py2py3 import is_bytes_or_string

from djpcms.conf import djpcms_defaults
from djpcms.utils.importer import import_module
from djpcms.ajaxhtml import ajaxhtml


class NoData(object):
    def __repr__(self):
        return '<NoData>'
    __str__ = __repr__
    
nodata = NoData()


class DjpcmsConfig(object):
    django_settings = None
    
    def __init__(self, settings_module_name, **kwargs):
        self.__dict__['_values'] = {}
        self.__dict__['_settings'] = []
        self.__dict__['settings_module_name'] = settings_module_name
        self.fill(djpcms_defaults)
        path = ''
        if self.settings_module_name:
            settings_module = import_module(settings_module_name)
            path = settings_module.__file__
            if path.endswith('.pyc'):
                path = path[:-1]
            self.fill(settings_module)
        self.__dict__['path'] = path
        self.update(kwargs)
        ajax = self.HTML_CLASSES
        if not ajax:
            self.HTML_CLASSES = ajaxhtml()
        de = self.DEFAULT_TEMPLATE_NAME
        if de:
            if is_bytes_or_string(de):
                de = (de,)
            else:
                de = tuple(de)
        else:
            de = ()
        self.DEFAULT_TEMPLATE_NAME = de
        
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
            if sett == sett.upper():
                default = v.get(sett, nodata)
                val     = getattr(mod, sett)
                if default is nodata or override:
                    v[sett] = val
                    
    def has(self, name):
        return name in self._settings
    
    def addsetting(self, setting):
        self._settings.append(setting)
        self.fill(setting,False)
        for sett,value in self._values.items():
            setattr(setting,sett,value)
        
    def get(self, name, default):
        try:
            return getattr(self,name)
        except AttributeError:
            return default
        
    def __getattr__(self, name):
        try:
            return self._values[name]
        except KeyError:
            raise AttributeError('Attribute {0} not available'.format(name))
    
    def __setattr__(self, name, value):
        self._values[name] = value
        for sett in self._settings:
            setattr(sett,name,value)
    
    def setup_django(self):
        '''Set up django if needed'''
        if self.__class__.django_settings:
            return
        if self.HTTP_LIBRARY == 'django' or \
            self.CMS_ORM == 'django' or self.TEMPLATE_ENGINE == 'django' or \
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
        
    
get_settings = DjpcmsConfig
