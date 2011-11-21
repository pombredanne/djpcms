from djpcms.utils import test
from djpcms import RegExUrl, IDREGEX


class TestRegExUrl(test.TestCase):
    
    def testRoot(self):
        r = RegExUrl('/')
        self.assertEqual(str(r),'^$')
        self.assertEqual(r.path,'/')
        r = RegExUrl('////')
        self.assertEqual(str(r),'^$')
        self.assertEqual(r.path,'/')
        r = RegExUrl()
        self.assertEqual(str(r),'^$')
        self.assertEqual(r.path,'/')
        
    def testSimple(self):
        r = RegExUrl('bla')
        self.assertEqual(str(r),'^bla/$')
        self.assertEqual(r.path,'/bla/')
        r += 'foo'
        self.assertEqual(str(r),'^bla/foo/$')
        self.assertEqual(r.path,'/bla/foo/')
        r = r + '/pinco///'
        self.assertEqual(str(r),'^bla/foo/pinco/$')
        self.assertEqual(r.path,'/bla/foo/pinco/')
        self.assertEqual(len(r.names),0)
        r = RegExUrl('bla') + RegExUrl('foo')
        self.assertEqual(str(r),'^bla/foo/$')
        self.assertEqual(r.path,'/bla/foo/')
        
    def testAppendSlashFalse(self):
        r = RegExUrl('bla', append_slash = False)
        self.assertEqual(str(r),'^bla')
        self.assertEqual(r.path,'/bla')
        r2 = RegExUrl('foo')
        self.assertEqual(str(r2),'^foo/$')
        self.assertEqual(r2.path,'/foo/')
        r3 = r2 + r
        self.assertEqual(str(r3),'^foo/bla')
        self.assertEqual(r3.path,'/foo/bla')
        self.assertFalse(r3.append_slash)
        r4 = RegExUrl('//foo//') + RegExUrl('///bla///', append_slash = False)
        self.assertEqual(str(r4),'^foo/bla')
        self.assertEqual(r4.path,'/foo/bla')
        self.assertFalse(r4.append_slash)
        self.assertRaises(ValueError, lambda : r + r2)

    def testVariables(self):
        r = RegExUrl('(?P<id>\d+)')
        self.assertEqual(str(r),'^(?P<id>\d+)/$')
        self.assertEqual(r.path,'/%(id)s/')
        self.assertEqual(len(r.names),1)
        self.assertEqual(r.names[0],'id')
        r2 = r + RegExUrl('(?P<name>[-\.\+\#\'\:\w]+)')
        self.assertEqual(str(r2),'^(?P<id>\d+)/(?P<name>[-\.\+\#\'\:\w]+)/$')
        self.assertEqual(r2.path,'/%(id)s/%(name)s/')
        self.assertEqual(len(r2.names),2)
        self.assertEqual(r2.names[0],'id')
        self.assertEqual(r2.names[1],'name')
    
    def testVariablesAppendSlashFalse(self):
        r1 = RegExUrl('doc')
        self.assertEqual(str(r1),'^doc/$')
        self.assertEqual(r1.path,'/doc/')
        #
        r2 = RegExUrl('(?P<path>[\w./-]*)',append_slash = False)
        self.assertEqual(str(r2),'^(?P<path>[\w./-]*)')
        self.assertEqual(r2.path,'/%(path)s')
        self.assertRaises(ValueError, lambda : r2 + r1)
        r3 = r1 + r2
        self.assertEqual(str(r3),'^doc/(?P<path>[\w./-]*)')
        self.assertEqual(r3.path,'/doc/%(path)s')
        self.assertFalse(r3.append_slash)
    
