from djpcms.template import make_default_inners


__all__ = ['PageMixin',
           'UserMixin']

class PageMixin(object):
    
    def makepage(self, url, **kwargs):
        from djpcms.models import Page
        page = Page(url = url, **kwargs)
        page.save()
        return page
    
    def makeInnerTemplates(self):
        from djpcms.models import InnerTemplate
        '''Create Inner templates from the ``djpcms/templates/djpcms/inner`` directory'''
        make_default_inners()
        return list(InnerTemplate.objects.all())
    
    
class UserMixin(TestCase):
        
    def makeusers(self):
        User = self.sites.User
        if User:
            self.superuser = User.create_super('testuser', 'test@testuser.com', 'testuser')
            self.user = User.create('simpleuser', 'simple@testuser.com', 'simpleuser')
        else:
            self.superuser = None
            self.user = None
        
    def login(self, username = None, password = None):
        if not username:
            return self.client.login(username = 'testuser', password = 'testuser')
        else:
            return self.client.login(username = username,password = password)