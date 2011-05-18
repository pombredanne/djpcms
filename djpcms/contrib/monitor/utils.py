from djpcms import sites
from djpcms.utils.importer import import_module

from stdnet import orm

__all__ = ['installed_models',
           'LINKED_OBJECT_ATTRIBUTE']

LINKED_OBJECT_ATTRIBUTE = 'djobject'



from stdnet.orm import model_iterator


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
            for mdl in model_iterator(label):
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
