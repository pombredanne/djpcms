from inspect import isclass

import djpcms

from sessions import PermissionBackend


class PermissionHandler(djpcms.PermissionHandler):
    '''Permission handler'''
    def __init__(self, backend = None, requires_login = False):
        self._backend = backend
        self.requires_login = requires_login
        
    @property
    def backend(self):
        if not self._backend:
            setts = djpcms.sites.settings or {}
            cname = setts.get('SESSION_COOKIE_NAME')
            sk = setts.get('SECRET_KEY')
            sexp = setts.get('SESSION_EXPIRY')
            self._backend = PermissionBackend(sk,cname,sexp)
        return self._backend
    
    def _has(self, request, permission_code, obj):
        if self.authenticated(request, obj, self.requires_login):
            if permission_code <= djpcms.VIEW:
                return True
            else:
                return request.user.is_superuser
        else:
            return False
        
    def has(self, request, permission_code, obj = None, model = None,
            view = None, user = None):
        if self._has(request,permission_code,obj):
            if not obj:
                return True
            if isclass(obj):
                model = obj
                obj = None
            else:
                model = obj.__class__
                return True
            #p = ObjectPermission.objects.filter(permission_model = model)
            #if not p.count():
            #    return None
        else:
            return False
    