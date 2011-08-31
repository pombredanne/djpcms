'''\
Permissions are controlled by the plugin the user provides.
'''

__all__ = ['PERMISSION_CODES',
           'PERMISSION_LIST',
           'VIEW',
           'ADD',
           'CHANGE',
           'DELETE',
           'DELETEALL',
           'addcode',
           'PermissionBackend',
           'SimplePermissionBackend',
           'SimpleLoginPermissionBackend']




# Main permission flags
VIEW = 10
ADD = 20
CHANGE = 30
DELETE = 40
DELETEALL = 50

PERMISSION_LIST = (
                   (VIEW,'VIEW'),
                   (ADD,'ADD'),
                   (CHANGE,'CHANGE'),
                   (DELETE,'DELETE'),
                   (DELETEALL,'DELETE ALL')
                  )
                    
PERMISSION_CODES = dict(PERMISSION_LIST)


def addcode(code,name):
    global PERMISSION_CODES
    try:
        code = int(code)
    except ValueError:
        return
    if code not in PERMISSION_CODES:
         PERMISSION_CODES[code] = name
         return code
     
     
class PermissionBackend(object):
        
    def permission_choices():
        global PERMISSION_CODES
        return ((k,PERMISSION_CODES[k]) for k in sorted(PERMISSION_CODES))
    
    def authenticated(self, request, obj, default = False):
        if getattr(obj,'requires_login',default):
            return request.user.is_authenticated()
        else:
            return True
    
    def has(self, request, permission_code, obj = None, model = None,
            view = None, user = None):
        raise NotImplementedError


class SimplePermissionBackend(PermissionBackend):
    
    def has(self, request, permission_code, obj = None, model = None,
            view = None, user = None):
        if self.authenticated(request,obj):
            if permission_code <= VIEW:
                return True
            else:
                return request.user.is_superuser
        else:
            return False
        

class SimpleLoginPermissionBackend(PermissionBackend):
    
    def has(self, request, permission_code, obj = None, model = None,
            view = None, user = None):
        if self.authenticated(request,obj,True):
            if permission_code <= VIEW:
                return True
            else:
                return request.user.is_superuser
        else:
            return False

