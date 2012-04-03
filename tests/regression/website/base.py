__test__ = False
from djpcms.utils import test


class TestCase(test.TestCase):
    
    def website(self):
        from djpsite.manage import WebSite
        from stdnet import orm
        self.orm = orm
        if not hasattr(self, 'site'):
            self._website = WebSite(config = 'djpsite.conf')
            self.site = self._website()
        return self._website
    
    def setUp(self):
        self.site = self.website()()
        self.assertTrue(self.orm.flush_models())
        
    def tearDown(self):
        self.orm.flush_models()
    
    def create_user(self, username='testuser', password='testuser',
                    is_superuser=True, login = False):
        user = self.site.permissions.create_user(username=username,
                                                 password=password,
                                                 is_superuser=is_superuser)
        self.assertEqual(user.username, username)
        return user
    
    def create_and_login(self, username='testuser', password='testuser',
                         **kwargs):
        user = self.create_user(username=username, password=password, **kwargs)
        data = {'username': user.username, 'password': password}
        c = self.client()
        request = c.post('/accounts/login', data=data)
        return c
    