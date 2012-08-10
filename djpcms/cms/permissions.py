'''Permissions are controlled by a :class:`PermissionHandler`

.. _api-permission-codes:

Permissions Codes
~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``VIEW`` This is the lowest level of permission. Value ``10``.
* ``CHANGE`` Allows to change/modify objects. Value ``20``.
* ``COPY`` Allows to copy objects into new ones. Value ``25``.
* ``ADD`` Allows to add new objects. Value ``30``.
'''
from pulsar.apps.wsgi import authorization_middleware
from .exceptions import PermissionDenied

# Main permission flags
# the higher the number the more restrictive the permission is
NONE = 0
VIEW = 10
CHANGE = 20
COPY = 25
ADD = 30
DELETE = 40
DELETEALL = 50
PERMISSION_LIST = [
                   (NONE, 'NONE'),
                   (VIEW, 'VIEW'),
                   (ADD, 'ADD'),
                   (COPY, 'COPY'),
                   (CHANGE, 'CHANGE'),
                   (DELETE, 'DELETE'),
                   (DELETEALL, 'DELETE ALL')
                  ]


class AuthenticationError(Exception):
    pass


class SimpleRobots(object):

    def __init__(self, settings):
        pass

    def __call__(self, request):
        if request.has_permission(user=None):
            #if not self.page or self.page.insitemap:
            return 'ALL'
        return 'NONE,NOARCHIVE'


class AuthBackend(object):
    '''Signature for :class:`AuthBackend` classes.'''
    def authenticate(self, environ, **params):
        pass

    def login(self, environ, user):
        pass

    def logout(self, environ, user):
        pass

    def get_user(self, *args, **kwargs):
        '''Retrieve a user.'''
        pass

    def create_user(self, *args, **kwargs):
        '''Create a standard user.'''
        pass

    def create_superuser(self, *args, **kwargs):
        '''Create a user with *superuser* permissions.'''
        pass

    def request_middleware(self):
        return ()

    def post_data_middleware(self):
        return ()

    def response_middleware(self):
        return ()


class PermissionHandler(object):
    '''Base class for permissions handlers.

:parameter settings: a settings dictionary.
:parameter auth_backends: set the :attr:`auth_backends`. If not provided, the
    :attr:`auth_backends` will be created by the :meth:`default_backends`.
:parameter requires_login: if ``True``, an authenticated user is always
    required.

.. attribute:: auth_backends

    A list of authentication backends. An authentication backend is an
    object which implements the :class:`AuthBackend` signature.

.. attribute:: requires_login

    boolean indicating if login is required to access resources.

    Default: ``False``.

.. attribute:: permission_codes

    A dictionary for mapping numeric codes into
    :ref:`permissions names <api-permission-codes>`. The higher the
    numeric code the more restrictive the permission is.
'''
    AuthenticationError = AuthenticationError

    def __init__(self, settings=None, auth_backends=None, requires_login=False):
        if auth_backends is None:
            auth_backends = self.default_backends(settings)
        self.auth_backends = auth_backends
        self.requires_login = requires_login
        self.permission_codes = dict(PERMISSION_LIST)

    def default_backends(self, settings):
        '''Create the default :class:`AuthBackend` list for this
:class:`PermissionHandler`. This function is invoked only if no
authentication backends are passed to the constructor.'''
        return []

    def request_middleware(self):
        '''Return a list of WSGI middlewares which are added to the WSGI
handler. These middlewares are obtained by the list of :attr:`auth_backends`.'''
        middleware = [self.process_request]
        for b in self.auth_backends:
            try:
                middleware.extend(b.request_middleware())
            except:
                pass
        return middleware

    def post_data_middleware(self):
        middleware = []
        for b in self.auth_backends:
            try:
                middleware.extend(b.post_data_middleware())
            except:
                pass
        return middleware

    def response_middleware(self):
        middleware = []
        for b in self.auth_backends:
            try:
                middleware.extend(b.response_middleware())
            except:
                pass
        return middleware

    def process_request(self, environ, start_response):
        '''Request middleware. Add self to the environment'''
        environ['permission_handler'] = self

    def addcode(self, code, name):
        '''Add a permission code to the list'''
        code = int(code)
        if code > 0:
             self.permission_codes[code] = name.upper()
             return code

    def permission_choices(self):
        c = self.permission_codes
        return ((k, c[k]) for k in sorted(c))

    def get_user(self, *args, **kwargs):
        '''Retrieve a user.'''
        for b in self.auth_backends:
            try:
                user = b.get_user(*args, **kwargs)
                if user is not None:
                    return user
            except:
                continue

    def authenticate_and_login(self, environ, **params):
        '''Authenticate and login user. If it fails raises
a AuthenticationError exception.'''
        user = self.authenticate(environ, **params)
        if user is not None and user.is_authenticated():
            if user.is_active:
                return self.login(environ, user)
            else:
                msg = '%s is not active' % user
        else:
            msg = 'username or password not recognized'
        raise ValueError(msg)

    def authenticate(self, environ, **params):
        for b in self.auth_backends:
            try:
                user = b.authenticate(environ, **params)
                if user is not None:
                    return user
            except:
                continue

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

    def create_superuser(self, *args, **kwargs):
        for b in self.auth_backends:
            try:
                user = b.create_superuser(*args, **kwargs)
                if user:
                    return user
            except:
                continue
        raise ValueError('Could not create superuser')

    def set_password(self, user, password):
        '''Loop though all :attr:`athentication_backends` and try to set
a new *password* for *user*. If it fails on all backends a ``ValueError``
is raised. User shouldn't need to override this function, instead they should
implement the :meth:`set_password` method on their authentication backend
if needed.

:parameter user: a user instance
:parameter password: the row password to assign to user.
'''
        success = False
        for b in self.auth_backends:
            try:
                b.set_password(user, password)
                success = True
            except:
                continue
        if not success:
            raise ValueError('Could not set password for user {0}'.format(user))

    def authenticated(self, request, instance, default=False):
        if getattr(instance, 'requires_login', default):
            return request.user.is_authenticated()
        else:
            return True

    def has(self, request, perm_code, instance=None, model=None, user=None):
        '''Check for permissions for a given request.

:parameter request: a :class:`djpcms.Request` instance.
:parameter perm_code: numeric code for permissions, the higher the code
    the more restrictive the permission. By default :mod:`djpcms` provides
    the :ref:`default permissions codes <api-permission-codes>`.

:parameter instance: optional instance of an object for which we require
    permission.
:parameter model: optional model class for which we require permission.
:parameter user: optional user for which we require permission.
'''
        return True

    def add_model(self, model):
        pass

    def header_authentication_middleware(self, environ, start_response):
        '''Middleware for basic Authentication via Header'''
        authorization_middleware(environ, start_response)
        auth = environ.get('HTTP_AUTHORIZATION')
        if auth:
            environ['user'] = self.authenticate(environ,
                                                username=auth.username,
                                                password=auth.password)

def authenticated_view(f):
    '''Decorator which check if a request is authenticated'''
    def _(self, request, *args, **kwargs):
        user = request.user
        if user and user.is_authenticated() and user.is_active:
            return f(self, request, *args, **kwargs)
        else:
            raise PermissionDenied()

    return _