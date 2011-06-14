from djpcms import sites
from djpcms.utils.importer import import_module
from djpcms.utils import lazyattr

from stdnet import orm
from stdnet.lib.redisinfo import RedisStats


__all__ = ['installed_models','DbQuery']


def installed_models(sites, applications = None):
    '''Generator of models classes.'''
    installed = sites.settings.INSTALLED_APPS
    applications = applications or installed
    for arg in applications:
        label = arg
        model = None
        argos = label.split('.')
        if len(argos) == 2:
            model = argos[1]
            label = argos[0]
        if label not in installed:
            label = 'djpcms.contrib.{0}'.format(label)
        if label in installed:
            for mdl in orm.model_iterator(label):
                if model:
                    if mdl._meta.name == model:
                        yield mdl
                        break
                else:
                    yield mdl
                    

def register_models(apps,**kwargs):
    '''Register models defined in application list ``apps``.'''
    all_apps = set()
    for app in sites.settings.INSTALLED_APPS:
        names = app.split('.')
        if names[0] == 'django':
            continue
        name = names[-1]
        all_apps.add(name)
        
    registered_models = []
    for name in apps:
        pm = name.split('.')
        models = None
        if len(pm) == 2:
            name = pm[0]
            models = (pm[1],)
        elif len(pm) > 2:
            raise ValueError('bad application {0}'.format(app))
        if name not in all_apps:
            raise ValueError('Application {0} not available'.format(app))
        try:
            import_module(name)
        except ImportError:
            name = 'djpcms.contrib.{0}'.format(name)
            try:
                import_module(name)
            except ImportError:
                continue
        registered_models.extend(orm.register_application_models(name,
                                                                 models = models,
                                                                 **kwargs))
    return registered_models


class DbQuery(object):
    
    def __init__(self, djp, r):
        self.djp   = djp
        self.r     = RedisStats(r)
        
    def __len__(self):
        return self.r.size()
    
    def __iter__(self):
        return self.data().__iter__()
    
    @lazyattr
    def data(self):
        return self.r.keys()
    
    def __getitem__(self, slic):
        data = self.data()[slic]
        type_length = self.r.type_length
        for key in data:
            keys = key.decode()
            typ,len,ttl = type_length(key)
            if ttl == -1:
                ttl = icons.no()
            yield (table_checkbox(keys,keys),typ,len,ttl)

