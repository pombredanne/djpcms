import os
from datetime import datetime

from .models import User, AnonymousUser, Session, get_session_cookie_name


def flush_session(request):
    '''Flush a session by expiring it. Return a new session.'''
    s = request.session
    s.expiry = datetime.now()
    s.save()
    request.session = Session.objects.create()


def authenticate(username = None, password = None, **kwargs):
    try:
        user = User.objects.get(username=username)
        if user.check_password(password):
            return user
    except User.DoesNotExist:
        return None
    

def login(request, user):
    """Store the user id on the session
    """
    user = user or request.user
    try:
        if request.session.user_id != user.id:
            flush_session(request)
    except KeyError:
        pass
    request.session.user_id = user.id


def logout(request):
    flush_session(request)
    request.user = AnonymousUser()


def get_user(request):
    try:
        user_id = request.session.user_id
    except KeyError:
        return AnonymousUser()
    try:
        return User.objects.get(id = user_id)
    except:
        flush_session(request)
        return AnonymousUser()


class SessionMiddleware(object):
    '''Djpcm middleware for sessions and authentication'''
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
        request.user = get_user(request)
        return None
    
    def process_response(self, request, response):
        """
        If request.session was modified, or if the configuration is to save the
        session every time, save the changes and set a session cookie.
        """
        session = request.session
        modified = getattr(session,'modified',True)
        if modified:
            response.set_cookie(get_session_cookie_name(),
                                session.id,
                                expires = session.expiry)
        return response
