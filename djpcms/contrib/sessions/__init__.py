'''\
Kitchen sink application for Users, Groups, Sessions and Permissions.
Based on python-stdnet for fast in-memory performance.
'''
import djpcms
from djpcms.apps import PERMISSION_CODES

from .models import ObjectPermission


class PermissionBackend(object):
    
    def has(self, request, permission_code, obj, user = None):
        if not obj:
            return None 
        if isclass(obj):
            model = obj
            obj = None
        else:
            model = obj.__class__
        p = ObjectPermission.objects.filter(permission_model = model)
        if not p.count():
            return None
        
        
def get_backends(backends = None):
    backends = backends
    if not backends and djpcms.sites.settings:
        backends = djpcms.sites.settings.AUTHENTICATION_BACKENDS
    if not backends:
        raise ImproperlyConfigured('No authentication backends have been defined. Does AUTHENTICATION_BACKENDS contain anything?')
    return [backend() for backend in backends]
        
        
def authenticate(**credentials):
    """If the given credentials are valid, return a User object.
    """
    for backend in get_backends():
        try:
            user = backend.authenticate(**credentials)
        except TypeError:
            # This backend doesn't accept these credentials as arguments. Try the next one.
            continue
        if user is None:
            continue
        # Annotate the user object with the path of the backend.
        user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
        return user

