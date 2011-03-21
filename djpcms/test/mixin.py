import os
import random
import hashlib
import time
          
from djpcms import to_bytestring
from djpcms.template import make_default_inners
from djpcms.utils import closedurl
from djpcms.apps.included.contentedit import PageForm
from djpcms.apps.included.user import create_user, create_superuser,\
                                      login, logout, authenticate


__all__ = ['PageMixin','UserMixin']



class DummySessionStore(dict):
    
    def __init__(self):
        super(DummySessionStore,self).__init__()
        pid = os.getpid()
        val = to_bytestring("%s%s%s" % (random.random(), pid, time.time()))
        self.session_key = hashlib.sha1(val).hexdigest()
        
    def flush(self):
        self.clear()
        
    def cycle_key(self):
        pass
    
    def save(self):
        pass
        


class PageMixin(object):
    
    def makepage(self, url, site = None, **kwargs):
        from djpcms.models import Page
        data = dict(PageForm.initials())
        data.update(kwargs)
        data['url'] = closedurl(url)
        site = site if site is not None else self.sites
        f = PageForm(model = Page, data = data, site = site)
        self.assertTrue(f.is_valid())
        return f.save()
    
    def makeInnerTemplates(self):
        from djpcms.models import InnerTemplate
        '''Create Inner templates from the ``djpcms/templates/djpcms/inner`` directory'''
        make_default_inners()
        return list(InnerTemplate.objects.all())
    
    
class UserMixin(object):
    session_cookie = 'test-session-cookie'
    session = None
        
    def makeusers(self):
        User = self.sites.User
        self.superuser = create_superuser(User, 'testuser', 'testuser', 'test@testuser.com')
        self.user = create_user(User, 'simpleuser', 'simpleuser', 'simple@testuser.com')
        
    def login(self, username = None, password = None):
        User = self.sites.User
        if not username:    
            user = authenticate(User, username = 'testuser', password = 'testuser')
        else:
            user = authenticate(User, username = username, password = password)
        if user and user.is_active:
            # Create a fake request to store login details.
            request = self.sites.http.make_request(self.client._base_environ())
            if not self.session:
                self.session = DummySessionStore()
                
            request.session = self.session
            
            login(User, request, user)

            # Save the session values.
            request.session.save()

            # Set the cookie to represent the session.
            cookies = self.client.cookies
            cookies[self.session_cookie] = request.session.session_key
            cookie_data = {
                'max-age': None,
                'path': '/',
                'domain': 'dummy',
                'secure': None,
                'expires': None,
            }
            cookies[self.session_cookie].update(cookie_data)

            return user
        
    def logout(self):
        logout(self.sites.User)
    