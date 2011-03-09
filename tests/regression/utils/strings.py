import unittest as test
from djpcms.utils import force_str, parentpath, closedurl, routejoin, openedurl
from djpcms.utils.text import nicename


__all__ = ['TestUtilsStrings',
           'TestUrls']


class TestUtilsStrings(test.TestCase):

    def test_force_str(self):
        ts = bytes('test string')
        self.assertEqual(force_str(ts),'test string')
        
    def testNiceName(self):
        self.assertEqual(nicename('ciao_bla'),'Ciao bla')
        self.assertEqual(nicename('ciao-bla_foo'),'Ciao bla foo')
        self.assertEqual(nicename('ciao bla-foo'),'Ciao bla foo')
        
class TestUrls(test.TestCase):
    
    def testParentpath(self):
        '''Test the parent path'''
        self.assertEqual(parentpath('/admin/pages/'),'/admin/')
        self.assertEqual(parentpath('/admin/pages'),'/admin/')
        self.assertEqual(parentpath('/admin/'),'/')
        self.assertEqual(parentpath('/admin'),'/')
        self.assertEqual(parentpath('/'),None)
        self.assertEqual(parentpath('/admin/bla/?db=6'),'/admin/')
        
    def testClosedUrl(self):
        self.assertEqual(closedurl('admin'),'/admin/')
        self.assertEqual(closedurl('admin///bla'),'/admin/bla/')
        self.assertEqual(closedurl('admin/'),'/admin/')
        self.assertEqual(closedurl('/admin'),'/admin/')
        self.assertEqual(closedurl(''),'/')
        self.assertEqual(closedurl('/'),'/')
        
    def testOpenedUrl(self):
        self.assertEqual(openedurl('/admin/'),'admin')
        self.assertEqual(openedurl('/admin/bla///'),'admin/bla')
        self.assertEqual(openedurl('/admin'),'admin')
        self.assertEqual(openedurl(''),'')
        self.assertEqual(openedurl('/'),'')

    def testroutejoin(self):
        self.assertEqual(routejoin('foo','bla'),'foo/bla')
        self.assertEqual(routejoin('foo','/bla'),'foo/bla')
        self.assertEqual(routejoin('foo/','/bla'),'foo/bla')
        self.assertEqual(routejoin('foo/','//bla////'),'foo/bla/')
        self.assertEqual(routejoin('////foo/','//bla////','pip'),'/foo/bla/pip')
        
