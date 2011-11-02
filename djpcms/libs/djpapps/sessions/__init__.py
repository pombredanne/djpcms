'''\
Kitchen sink application for Users, Groups, Sessions and Permissions.
Based on python-stdnet for fast in-memory performance.
'''
from inspect import isclass
from datetime import datetime

import djpcms

from .models import ObjectPermission, User, Session, AnonymousUser,\
                     get_session_cookie_name


class PermissionBackend(djpcms.PermissionBackend):
    '''Permission backend'''
    
    def __init__(self, requires_login = False, secret_key = None):
        self.requires_login = requires_login
        self.secret_key = secret_key
    
    def _has(self, request, permission_code, obj):
        if self.authenticated(request,obj,self.requires_login):
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
        request.session = Session.objects.create()
        
    def get_user(self, request):
        try:
            user_id = request.session.user_id
        except KeyError:
            return AnonymousUser()
        try:
            return User.objects.get(id = user_id)
        except:
            self.flush_session(request)
            return AnonymousUser()
        
    def login(self, request, user):
        """Store the user id on the session
        """
        user = user or request.user
        try:
            if request.session.user_id != user.id:
                self.flush_session(request)
        except KeyError:
            pass
        request.session.user_id = user.id
    
    def logout(self, request):
        self.flush_session(request)
        request.user = AnonymousUser()
        
    def create_user(self, *args, **kwargs):
        return User.objects.create_user(*args, **kwargs)
    
    def create_superuser(self, *args, **kwargs):
        return User.objects.create_superuser(*args, **kwargs)
        
    def process_request(self, request):
        cookie_name = get_session_cookie_name()
        session_key = request.COOKIES.get(cookie_name, None)
        if not (session_key and Session.objects.exists(session_key)):
            session = Session.objects.create()
            session.modified = True
        else:
            session = Session.objects.get(id = session_key)
            session.modified = False
        request.session = session
        request.user = self.get_user(request)
        return None
    
    def process_response(self, request, response):
        """If request.session was modified set a session cookie.
        """
        session = request.session
        modified = getattr(session,'modified',True)
        if modified:
            response.set_cookie(get_session_cookie_name(),
                                session.id,
                                expires = session.expiry)
        return response


