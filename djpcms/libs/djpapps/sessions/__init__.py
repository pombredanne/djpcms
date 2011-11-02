'''\
Kitchen sink application for Users, Groups, Sessions and Permissions.
Based on python-stdnet for fast in-memory performance.
'''
import sys
from datetime import datetime

from .models import ObjectPermission, User, Session, AnonymousUser

ispy3k = int(sys.version[0]) >= 3

if ispy3k:
    from http.cookies import SimpleCookie, CookieError, BaseCookie
else:
    from Cookie import SimpleCookie, CookieError, BaseCookie


SESSION_COOKIE_NAME = 'stdnet-sessionid'


class PermissionBackend(object):
    '''Permission backend
    
.. attribute:: secret_key

    Secret key for encryption SALT
    
.. attribute:: session_cookie_name

    Session cokie name
    
.. attribute:: session_expiry

    Session expiry in seconds
    
    Default: 2 weeks
    
'''
    
    def __init__(self,
                 secret_key = None,
                 session_cookie_name = None,
                 session_expiry = None):
        self.secret_key = secret_key
        self.session_cookie_name = session_cookie_name or SESSION_COOKIE_NAME
        self.session_expiry = session_expiry or 14*24*3600
    
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def flush_session(self, request):
        '''Flush a session by expiring it. Return a new session.'''
        s = request.session
        s.expiry = datetime.now()
        s.save()
        request.session = Session.objects.create(self.session_expiry)
        
    def get_user(self, environ):
        try:
            user_id = environ['session'].user_id
        except KeyError:
            return AnonymousUser()
        try:
            return User.objects.get(id = user_id)
        except:
            self.flush_session(request)
            return AnonymousUser()
        
    def login(self, environ, user):
        """Store the user id on the session
        """
        user = user or environ.get('user')
        try:
            if environ['session'].user_id != user.id:
                self.flush_session(request)
        except KeyError:
            pass
        environ['session'].user_id = user.id
    
    def logout(self, request):
        self.flush_session(request)
        request.user = AnonymousUser()
        
    def create_user(self, *args, **kwargs):
        return User.objects.create_user(*args, **kwargs)
    
    def create_superuser(self, *args, **kwargs):
        return User.objects.create_superuser(*args, **kwargs)
        
    def get_cookie(self, environ, start_response):
        c = environ.get('HTTP_COOKIE', '')
        if not isinstance(c,dict):
            if not isinstance(c,str):
                c = c.encode('utf-8')
            c = parse_cookie(c)
            environ['HTTP_COOKIE'] = c
            
    def request_middleware(self):
        return [self.get_cookie,
                self.process_request]
    
    def process_request(self, environ, start_response):
        cookie_name = self.session_cookie_name
        cookie = self.get_cookie(environ)
        session_key = cookie.get(cookie_name, None)
        if not (session_key and Session.objects.exists(session_key)):
            session = Session.objects.create(self.session_expiry)
            session.modified = True
        else:
            session = Session.objects.get(id = session_key)
            session.modified = False
        environ['session'] = session
        environ['user'] = self.get_user(environ)
    
    def process_response(self, request, response):
        """If request.session was modified set a session cookie.
        """
        session = request.session
        modified = getattr(session,'modified',True)
        if modified:
            response.set_cookie(self.session_cookie_name,
                                session.id,
                                expires = session.expiry)
        return response



def parse_cookie(cookie):
    if cookie == '':
        return {}
    if not isinstance(cookie, BaseCookie):
        try:
            c = SimpleCookie()
            c.load(cookie)
        except CookieError:
            # Invalid cookie
            return {}
    else:
        c = cookie
    cookiedict = {}
    for key in c.keys():
        cookiedict[key] = c.get(key).value
    return cookiedict