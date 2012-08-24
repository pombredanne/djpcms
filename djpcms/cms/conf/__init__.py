import os

from djpcms.utils.httpurl import is_string_or_native_string
from djpcms.utils.importer import import_module

from . import defaults


class Config(object):

    def __init__(self, settings_module_name, **kwargs):
        self.__dict__['_values'] = {}
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
        site_module = self.get('SITE_MODULE')
        apps = ['djpcms']
        for app in self.INSTALLED_APPS:
            if app not in apps and app != site_module:
                apps.append(app)
        if site_module:
            apps.append(site_module)
        self.INSTALLED_APPS = tuple(apps)

    def __repr__(self):
        return self._values.__repr__()
    __str__  = __repr__

    def update(self, mapping):
        v = self._values
        for sett,val in mapping.items():
            if sett == sett.upper():
                v[sett] = val

    def fill(self, mod, override=True):
        v = self._values
        for sett in dir(mod):
            if sett.startswith('_'):
                continue
            setts = sett.split('__')
            s = setts[0]
            if s and s == s.upper():
                d = v
                for s in setts[:-1]:
                    if s not in d:
                        d[s] = {}
                    d = d[s]
                s = setts[-1]
                if s not in d or override:
                    d[s] = getattr(mod, sett)

    def get(self, name, default=None):
        return self._values.get(name, default)

    def __getstate__(self):
        return self.__dict__.copy()

    def __setstate__(self, state):
        for k,v in state.items():
            self.__dict__[k] = v

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


