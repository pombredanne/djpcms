import djpcms
from djpcms import PermissionHandler
from djpcms.utils import test


class useless_backend(object):
    pass
    
class TestSites(test.TestCase):
    
    def testSimple(self):
        p = PermissionHandler({})
        self.assertEqual(p.auth_backends, [])
        self.assertEqual(p.requires_login , False)
        middleware = p.request_middleware()
        self.assertEqual(len(middleware),1)
        r = {}
        middleware[0](r,None)
        self.assertEqual(r['permission_handler'],p)
        
    def testUseless(self):
        p = PermissionHandler({},
                              auth_backends=[useless_backend()])
        self.assertEqual(len(p.auth_backends), 1)
        middleware = p.request_middleware()
        self.assertEqual(len(middleware),1)
        self.assertEqual(p.authenticate(None), None)
        self.assertEqual(p.login({}, None), None)
        self.assertEqual(p.logout({}), None)
        self.assertRaises(ValueError, p.authenticate_and_login, {})
        self.assertRaises(ValueError, p.create_user)
        self.assertRaises(ValueError, p.set_password, 'luca', 'bla')
        