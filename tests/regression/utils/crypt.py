import unittest as test
import base64

from djpcms.utils import rc4crypt, encrypt, decrypt

try:
    import cPickle as pickle
except ImportError:
    import pickle


class TestArc4(test.TestCase):
    
    def testCript(self):
        data = b'pippo-pass'
        key = b'blabla'
        v = rc4crypt(data,key)
        self.assertTrue(v)
        v2 = rc4crypt(v,key)
        self.assertTrue(v2)
        self.assertEqual(data,v2)
        
    def testCript2(self):
        key = b'blabla'
        data = b'pippo-pass'
        k = encrypt(data,key)
        stored = pickle.dumps(k)
        
        # Reversed
        v2 = decrypt(pickle.loads(stored),key)
        self.assertEqual(data,v2)