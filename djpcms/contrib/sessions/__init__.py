from .models import ObjectPermission

from djpcms.apps import PERMISSION_CODES


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