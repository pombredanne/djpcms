import unittest as test

from djpcms.utils.structures import MultiValueDict



class TestMultiValueDict(test.TestCase):
    
    def testConstructor(self):
        m = MultiValueDict()
        self.assertEqual(len(m), 0)
        m = MultiValueDict({'bla': 3})
        self.assertEqual(len(m), 1)
        self.assertEqual(m['bla'], 3)
        m = MultiValueDict({'bla': (3,78), 'foo': 'ciao'})
        self.assertEqual(len(m), 2)
        self.assertEqual(m['bla'], [3,78])
        self.assertEqual(m['foo'], 'ciao')
        
    def testset(self):
        m = MultiValueDict()
        m['bla'] = 5
        m['bla'] = 89
        self.assertEqual(m['bla'], [5,89])
        