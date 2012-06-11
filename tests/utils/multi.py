import unittest as test

from djpcms.utils.structures import MultiValueDict


class TestMultiValueDict(test.TestCase):
    
    def testConstructor(self):
        m = MultiValueDict()
        self.assertEqual(len(m), 0)
        #
        m = MultiValueDict({'bla': 3})
        self.assertEqual(len(m), 1)
        self.assertEqual(m['bla'], 3)
        #
        m = MultiValueDict({'bla': (3,78), 'foo': 'ciao'})
        self.assertEqual(len(m), 2)
        self.assertEqual(m['bla'], [3,78])
        self.assertEqual(m['foo'], 'ciao')
        #
        m = MultiValueDict({'bla': [3,78], 'foo': (v for v in (1,2))})
        self.assertEqual(m['bla'], [3,78])
        self.assertEqual(m['foo'], [1,2])
        
    def testset(self):
        m = MultiValueDict()
        m['bla'] = 5
        m['bla'] = 89
        self.assertEqual(m['bla'], [5,89])
        m['foo'] = 'pippo'
        self.assertEqual(m['foo'], 'pippo')
        return m
    
    def testextra(self):
        m = MultiValueDict()
        m.setdefault('bla','foo')
        self.assertEqual(m['bla'],'foo')
        m['bla'] = 'ciao'
        self.assertEqual(m['bla'],['foo','ciao'])
    
    def testget(self):
        m = self.testset()
        self.assertEqual(m.get('sdjcbhjcbh'),None)
        self.assertEqual(m.get('sdjcbhjcbh','ciao'),'ciao')
        
    def testupdate(self):
        m = self.testset()
        m.update({'bla':'star',5:'bo'})
        self.assertEqual(m['bla'],[5,89,'star'])
        self.assertEqual(m[5],'bo')
        
    def test_iterators(self):
        m = self.testset()
        d = dict(m.items())
        self.assertEqual(d['bla'],[5,89])
        self.assertEqual(d['foo'],'pippo')
        l = list(m.values())
        self.assertEqual(len(l), 2)
        self.assertTrue([5,89] in l)
        self.assertTrue('pippo' in l)
    
    def testlists(self):
        m = self.testset()
        items = dict(m.lists())
        self.assertEqual(len(items),2)
        for k,v in items.items():
            self.assertTrue(isinstance(v,list))
        self.assertEqual(items['bla'], [5,89])
        self.assertEqual(items['foo'], ['pippo'])
        
    def testCopy(self):
        m = self.testset()
        m2 = m.copy()
        self.assertEqual(m2['bla'], [5,89])
        self.assertEqual(m2['foo'], 'pippo')
        self.assertEqual(m2.getlist('foo'), ['pippo'])
        