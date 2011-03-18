import unittest as test
from djpcms.views import RegExUrl, IDREGEX


class TestRegExUrl(test.TestCase):
    
    def testRoot(self):
        r = RegExUrl('/')
        self.assertEqual(r.url,'')
        self.assertEqual(str(r),'^$')
        self.assertEqual(r.purl,'')
        r = RegExUrl('////')
        self.assertEqual(r.url,'')
        self.assertEqual(str(r),'^$')
        self.assertEqual(r.purl,'')
        r = RegExUrl()
        self.assertEqual(r.url,'')
        self.assertEqual(str(r),'^$')
        self.assertEqual(r.purl,'')
        
    def testSimple(self):
        r = RegExUrl('bla')
        self.assertEqual(r.url,'bla/')
        self.assertEqual(str(r),'^bla/$')
        self.assertEqual(r.purl,'bla/')
        r += 'foo'
        self.assertEqual(r.url,'bla/foo/')
        self.assertEqual(str(r),'^bla/foo/$')
        self.assertEqual(r.purl,'bla/foo/')
        r = r + '/pinco///'
        self.assertEqual(r.url,'bla/foo/pinco/')
        self.assertEqual(str(r),'^bla/foo/pinco/$')
        self.assertEqual(r.purl,'bla/foo/pinco/')
        self.assertEqual(len(r.names),0)
        r = RegExUrl('bla') + RegExUrl('foo')
        self.assertEqual(r.url,'bla/foo/')
        self.assertEqual(str(r),'^bla/foo/$')
        self.assertEqual(r.purl,'bla/foo/')
        
    def testAppendSlashFalse(self):
        r = RegExUrl('bla', append_slash = False)
        self.assertEqual(r.url,'bla')
        self.assertEqual(str(r),'^bla')
        self.assertEqual(r.purl,'bla')
        r2 = RegExUrl('foo')
        self.assertEqual(r2.url,'foo/')
        self.assertEqual(str(r2),'^foo/$')
        self.assertEqual(r2.purl,'foo/')
        r3 = r2 + r
        self.assertEqual(r3.url,'foo/bla')
        self.assertEqual(str(r3),'^foo/bla')
        self.assertEqual(r3.purl,'foo/bla')
        self.assertFalse(r3.append_slash)
        r4 = RegExUrl('//foo//') + RegExUrl('///bla///', append_slash = False)
        self.assertEqual(r4.url,'foo/bla')
        self.assertEqual(str(r4),'^foo/bla')
        self.assertFalse(r4.append_slash)
        self.assertRaises(ValueError, lambda : r + r2)

    def testVariables(self):
        r = RegExUrl('(?P<id>\d+)')
        self.assertEqual(r.url,'(?P<id>\d+)/')
        self.assertEqual(str(r),'^(?P<id>\d+)/$')
        self.assertEqual(r.purl,'%(id)s/')
        self.assertEqual(len(r.names),1)
        self.assertEqual(r.names[0],'id')
        r2 = r + RegExUrl('(?P<name>[-\.\+\#\'\:\w]+)')
        self.assertEqual(r2.url,'(?P<id>\d+)/(?P<name>[-\.\+\#\'\:\w]+)/')
        self.assertEqual(str(r2),'^(?P<id>\d+)/(?P<name>[-\.\+\#\'\:\w]+)/$')
        self.assertEqual(r2.purl,'%(id)s/%(name)s/')
        self.assertEqual(len(r2.names),2)
        self.assertEqual(r2.names[0],'id')
        self.assertEqual(r2.names[1],'name')
    
    def testVariablesAppendSlashFalse(self):
        r1 = RegExUrl('doc')
        r2 = RegExUrl('(?P<path>[\w./-]*)',append_slash = False)
        self.assertEqual(r2.url,'(?P<path>[\w./-]*)')
        self.assertEqual(str(r2),'^(?P<path>[\w./-]*)')
        self.assertEqual(r2.purl,'%(path)s')
        self.assertRaises(ValueError, lambda : r2 + r1)
        r3 = r1 + r2
        self.assertEqual(r3.url,'doc/(?P<path>[\w./-]*)')
        self.assertEqual(str(r3),'^doc/(?P<path>[\w./-]*)')
        self.assertEqual(r3.purl,'doc/%(path)s')
        self.assertFalse(r3.append_slash)
    
