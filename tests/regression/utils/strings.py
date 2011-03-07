import unittest as test
from djpcms.utils import force_str, parentpath


__all__ = ['TestUtilsStrings',
           'TestUrls']


class TestUtilsStrings(test.TestCase):

    def test_force_str(self):
        ts = bytes('test string')
        self.assertEqual(force_str(ts),'test string')
        
        
class TestUrls(test.TestCase):
    
    def testParentpath(self):
        '''Test the parent path'''
        self.assertEqual(parentpath('/admin/pages/'),'/admin/')
        self.assertEqual(parentpath('/admin/pages'),'/admin/')
        self.assertEqual(parentpath('/admin/'),'/')
        self.assertEqual(parentpath('/admin'),'/')
        self.assertEqual(parentpath('/'),None)
        self.assertEqual(parentpath('/admin/bla/?db=6'),'/admin/')
