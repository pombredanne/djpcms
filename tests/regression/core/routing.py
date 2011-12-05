from djpcms.utils import test
from djpcms import Route, UrlException

    
class Routes(test.TestCase):
    
    def testRoot(self):
        r = Route('/')
        self.assertFalse(r.is_leaf)
        self.assertEqual(r.rule,'')
        r = Route('////')
        self.assertFalse(r.is_leaf)
        self.assertEqual(r.rule,'')
        self.assertEqual(r.match(''),{})
        self.assertEqual(r.match('bee/'),{'__remaining__':'bee/'})
        
    def testSimple(self):
        r = Route('bla/')
        self.assertFalse(r.is_leaf)
        self.assertEqual(len(r.arguments),0)
        self.assertEqual(r.rule,'bla/')
        self.assertEqual(r.match('bla/'),{})
        self.assertEqual(r.match('bladdd/'),None)
        self.assertEqual(r.match('bla/another/'),{'__remaining__':'another/'})
        
    def testSimpleAppendSlash(self):
        r = Route('bla', append_slash = True)
        self.assertFalse(r.is_leaf)
        self.assertEqual(r.rule,'bla/')
        
    def testStringVariable(self):
        r = Route('<name>/')
        self.assertFalse(r.is_leaf)
        self.assertEqual(r.arguments,set(['name']))
        self.assertEqual(r.breadcrumbs,[(True,'name')])
        self.assertEqual(r.rule,'<name>/')
        self.assertEqual(r.match('bla-foo/'),{'name':'bla-foo'})
        self.assertEqual(r.match('bla/another/'),{'name':'bla',
                                                   '__remaining__':'another/'})
        self.assertEqual(r.url(name = 'luca'),'/luca/')
        
    def test2StringVariables(self):
        r = Route('<name>/<child>/')
        self.assertFalse(r.is_leaf)
        self.assertEqual(r.arguments,set(['name','child']))
        self.assertEqual(r.breadcrumbs,[(True,'name'),(True,'child')])
        self.assertEqual(r.rule,'<name>/<child>/')
        self.assertEqual(r.match('bla/foo/'),{'name':'bla','child':'foo'})
        self.assertEqual(r.match('bla/foo/another/'),
                         {'name':'bla','child':'foo',
                          '__remaining__':'another/'})
        self.assertRaises(KeyError, lambda : r.url(name = 'luca'))
        self.assertEqual(r.url(name = 'luca', child = 'joshua'),
                         '/luca/joshua/')
        
    def testAddDirLeaf(self):
        r = Route('bla/')
        self.assertFalse(r.is_leaf)
        r2 = Route('foo')
        self.assertTrue(r2.is_leaf)
        r3 = r + r2
        self.assertEqual(r3.rule,'bla/foo')
        self.assertTrue(r3.is_leaf)
        
    def testIntVariable(self):
        r = Route('<int:id>/')
        self.assertEqual(str(r),'/<int:id>/')
        self.assertEqual(r.arguments,set(['id']))
        self.assertEqual(r.breadcrumbs,[(True,'id')])
        self.assertEqual(r.match('35/'),{'id':35})
        self.assertEqual(r.url(id = 1), '/1/')
        self.assertRaises(ValueError,lambda : r.url(id = 'bla'))
        
    def testIntVariableFixDigits(self):
        r = Route('<int(2):id>/')
        self.assertEqual(str(r),'/<int(2):id>/')
        self.assertEqual(r.arguments,set(['id']))
        self.assertEqual(r.breadcrumbs,[(True,'id')])
        self.assertEqual(r.match('35/'),{'id':35})
        self.assertEqual(r.match('355/'),None)
        self.assertEqual(r.match('6/'),None)
        self.assertEqual(r.match('ch/'),None)
        self.assertEqual(r.url(id = 13), '/13/')
        self.assertEqual(r.url(id = 1), '/01/')
        self.assertRaises(ValueError,lambda : r.url(id = 134))
        self.assertRaises(ValueError,lambda : r.url(id = 'bl'))
        self.assertRaises(ValueError,lambda : r.url(id = 'bla'))
        
    def testIntVariableMinMax(self):
        r = Route('<int(min=1):cid>/')
        self.assertEqual(str(r),'/<int(min=1):cid>/')
        self.assertEqual(r.arguments,set(['cid']))
        self.assertEqual(r.breadcrumbs,[(True,'cid')])
        self.assertEqual(r.match('1/'),{'cid':1})
        self.assertEqual(r.match('476876/'),{'cid':476876})
        self.assertEqual(r.match('0/'),None)
        self.assertEqual(r.match('-5/'),None)
        self.assertEqual(r.url(cid = 13), '/13/')
        self.assertEqual(r.url(cid = 1), '/1/')
        self.assertRaises(ValueError,lambda : r.url(cid = 0))
        self.assertRaises(ValueError,lambda : r.url(cid = -10))
        self.assertRaises(ValueError,lambda : r.url(cid = 'bla'))
        
    def testPathVaiable(self):
        r = Route('bla/<path:rest>', defaults = {'rest':''})
        self.assertEqual(r.arguments,set(['rest']))
        self.assertEqual(len(r.breadcrumbs),2)
        self.assertTrue(r.is_leaf)
        self.assertEqual(r.match('bla/a/b/c.html'),{'rest':'a/b/c.html'})
        self.assertEqual(r.match('bla/'),{'rest':''})
        self.assertEqual(r.url(rest = 'a/'), '/bla/a/')
        self.assertEqual(r.url(), '/bla/')
        
    def testSplitRoot(self):
        r = Route('')
        p,l = r.split()
        self.assertFalse(p.is_leaf)
        self.assertEqual(p.path,'/')
        self.assertEqual(l,None)
        r = Route('bla')
        p,l = r.split()
        self.assertFalse(p.is_leaf)
        self.assertTrue(l.is_leaf)
        self.assertEqual(p.path,'/')
        self.assertEqual(l.path,'/bla')
        r = Route('bla/')
        p,l = r.split()
        self.assertFalse(p.is_leaf)
        self.assertFalse(l.is_leaf)
        self.assertEqual(p.path,'/')
        self.assertEqual(l.path,'/bla/')
        
    def testSplitDir(self):
        r = Route('bla/foo/<id>/pluto/')
        p,l = r.split()
        self.assertFalse(p.is_leaf)
        self.assertFalse(l.is_leaf)
        self.assertEqual(p.path,'/bla/foo/<id>/')
        self.assertEqual(l.path,'/pluto/')
        
    def testSplitLeaf(self):
        r = Route('bla/foo/<id>/pluto/leaf')
        p,l = r.split()
        self.assertFalse(p.is_leaf)
        self.assertTrue(l.is_leaf)
        self.assertEqual(p.path,'/bla/foo/<id>/pluto/')
        self.assertEqual(l.path,'/leaf')
        
    def testDefaults(self):
        r = Route('bla/<id>/add/<path:path>',{'path':''})
        self.assertEqual(r.url(id=10),'/bla/10/add/')
        self.assertEqual(r.url(id=10,path='ciao/luca'),'/bla/10/add/ciao/luca')
        
    def testDefaultsAddition(self):
        r = Route('add/<path:path>',{'path':''})
        r2 = Route('bla/<id>/') + r
        self.assertEqual(r2.defaults,r.defaults)