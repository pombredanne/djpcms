'''\
Permissions are controlled by the plugin the user provides.
'''

__all__ = ['PERMISSION_CODES',
           'PERMISSION_LIST',
           'VIEW',
           'ADD',
           'COPY',
           'CHANGE',
           'DELETE',
           'DELETEALL',
           'addcode',
           'PermissionHandler',
           'SimpleRobots']




# Main permission flags
VIEW = 10
ADD = 20
COPY = 25
CHANGE = 30
DELETE = 40
DELETEALL = 50


PERMISSION_LIST = [
                   (VIEW,'VIEW'),
                   (ADD,'ADD'),
                   (COPY,'COPY'),
                   (CHANGE,'CHANGE'),
                   (DELETE,'DELETE'),
                   (DELETEALL,'DELETE ALL')
                  ]
                    
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
     

class AuthenticationError(Exception):
    pass


class SimpleRobots(object):
    
    def __call__(self, request):
        if request.has_permission(user = None):
            #if not self.page or self.page.insitemap:
            return 'ALL'
        return 'NONE,NOARCHIVE'
     
     
class PermissionHandler(object):
    '''Base class for permissions handler.
    
.. attribute:: backend

    an instance of a Permission backend
'''
    AuthenticationError = AuthenticationError
    backend = None
    
    def permission_choices():
        return ((k,PERMISSION_CODES[k]) for k in sorted(PERMISSION_CODES))
    
    def authenticated(self, request, obj, default = False):
        if getattr(obj,'requires_login',default):
            return request.user.is_authenticated()
        else:
            return True
    
    def has(self, request, permission_code, obj = None, model = None,
            view = None, user = None):
        '''Check for permissions for a given request.
        
:parameter request: a wsgi :class:`djpcms.Request` instance.
:parameter permission_code: numeric code for permissions, the higher the code
    the more restrictive is permission.
:parameter obj: optional instance of an object for which we require permission.
:parameter model: optional model class for which we require permission.
:parameter view: optional user for which we require permission.
'''
        return True

