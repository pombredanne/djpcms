from djpcms.utils import test


class TestPermissions(test.TestCase):

    def testList(self):
        from djpcms.cms import permissions
        hnd = permissions.PermissionHandler()
        self.assertTrue(10 in hnd.permission_codes)
        self.assertFalse(15 in hnd.permission_codes)
        self.assertEqual(hnd.addcode(15, 'calculate'), 15)
        self.assertTrue(15 in hnd.permission_codes)
        self.assertEqual(hnd.permission_codes[15], 'CALCULATE')

    def testCreateUser(self):
        from djpcms.cms import permissions
        hnd = permissions.PermissionHandler()
        self.assertEqual(hnd.create_user(username='bla', password='foo'), None)
