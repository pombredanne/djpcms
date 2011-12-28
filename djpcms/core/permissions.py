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
           'SimpleRobots',
           'authenticated_view']


from .exceptions import PermissionDenied



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
    
    def __init__(self, settings):
        pass
    
    def __call__(self, request):
        if request.has_permission(user = None):
            #if not self.page or self.page.insitemap:
            return 'ALL'
        return 'NONE,NOARCHIVE'
     
     
class PermissionHandler(object):
    '''Base class for permissions handlers.
    
:parameter settings: a settings dictionary.
:parameter auth_backends: set the :attr:`auth_backends`. If not provided, the
    :attr:`auth_backends` will be created by the :meth:`default_backends`.
:parameter requires_login: if ``True``, an authenticated user is always
    required.
    
.. attribute:: auth_backends

    an iterable over authentication backends.
    

.. attribute:: requires_login

    boolean indicating if login is required.
    
'''
    AuthenticationError = AuthenticationError
    
    def __init__(self, settings, auth_backends = None, requires_login = False):
        if auth_backends is None:
            auth_backends = self.default_backends(settings)
        self.auth_backends = auth_backends
        self.requires_login = requires_login
    
    def default_backends(self, settings):
        '''Create the default authentication backends.'''
        return []
    
    def authenticate(self, request, **params):
        for b in self.auth_backends:
            try:
                user = b.authenticate(request, **params)
                if user is not None:
                    return user
            except:
                continue
            
    def authenticate_and_login(self, environ, **params):
        '''authenticate and login user. If it fails raises
a AuthenticationError exception.'''
        user = self.authenticate(environ, **params)
        if user is not None and user.is_authenticated():
            if user.is_active:
                return self.login(environ, user)
            else:
                msg = '%s is not active' % username
        else:
            msg = 'username or password not recognized'
        raise ValueError(msg)
    
    def login(self, environ, user):
        for b in self.auth_backends:
            try:
                u = b.login(environ, user)
                if u is not None:
                    return u
            except:
                continue
            
    def logout(self, environ):
        '''Logout user'''
        for b in self.auth_backends:
            try:
                if b.logout(environ):
                    return True
            except:
                continue
            
    def create_user(self, *args, **kwargs):
        for b in self.auth_backends:
            try:
                user = b.create_user(*args, **kwargs)
                if user:
                    return user
            except:
                continue
        raise ValueError('Could not create user')
    
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
        
:parameter request: a :class:`djpcms.Request` instance.
:parameter permission_code: numeric code for permissions, the higher the code
    the more restrictive the permission. By default :mod:`djpcms` provides
    the following codes::
    
        VIEW = 10
        ADD = 20
        COPY = 25
        CHANGE = 30
        DELETE = 40
        DELETEALL = 50
        
:parameter obj: optional instance of an object for which we require permission.
:parameter model: optional model class for which we require permission.
:parameter user: optional user for which we require permission.
'''
        return True


def authenticated_view(f):
    
    def _(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated() and user.is_active:
            return f(self, request, *args, **kwargs)
        else:
            raise PermissionDenied()

    return _