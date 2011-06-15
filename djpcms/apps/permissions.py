

__all__ = ['PERMISSION_CODES',
           'PERMISSION_LIST',
           'VIEW',
           'ADD',
           'CHANGE',
           'DELETE',
           'addcode',
           'PermissionBackend']




# Main permission flags
VIEW = 10
ADD = 20
CHANGE = 30
DELETE = 40

PERMISSION_LIST = (
                   (VIEW,'VIEW'),
                   (ADD,'ADD'),
                   (CHANGE,'CHANGE'),
                   (DELETE,'DELETE')
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
    
    def has(self, request, permission_code, obj = None, model = None,
            view = None, user = None):
        raise NotImplementedError


class SimplePermissionBackend(PermissionBackend):
    
    def has(self, request, permission_code, obj = None, model = None,
            view = None, user = None):
        if permission_code <= VIEW:
            return True
        else:
            return request.user.is_superuser
        
        