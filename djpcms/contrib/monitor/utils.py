from djpcms import sites

from stdnet import orm


def register_models(apps,**kwargs):
    '''Register models defined in application list ``apps``.'''
    all_apps = {}
    for app in sites.settings.INSTALLED_APPS:
        names = app.split('.')
        if names[0] == 'django':
            continue
        name = names[-1]
        if name in all_apps:
            raise ValueError('multiple application name {0}'.format(name))
        all_apps[name] = app
        
    registered_models = []
    for name in apps:
        pm = name.split('.')
        models = None
        if len(pm) == 2:
            name = pm[0]
            models = (pm[1],)
        elif len(pm) > 2:
            raise Valuerror('bad application {0}'.format(app))
        if name not in all_apps:
            raise Valuerror('Application {0} not available'.format(app))
        app = all_apps[name]
        registered_models.extend(orm.register_application_models(name,
                                                                 models = models,
                                                                 **kwargs))
    return registered_models