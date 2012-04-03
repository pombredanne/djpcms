from djpcms.utils import test
from djpcms.utils.async import Deferred, MultiDeferred


class TestMultiDeferred(test.TestCase):
    
    def testSimple(self):
        m = MultiDeferred()
        self.assertFalse(m._locked)
        self.assertTrue(isinstance(m._stream,list))
        m.update([1,3,4])
        self.assertFalse(m._locked)
        m.lock()
        self.assertTrue(m._locked)
        self.assertTrue(m.called)
        self.assertEqual(m.result,[1,3,4])
        
    def testCallaback(self):
        m = MultiDeferred()
        m2 = Deferred()
        m.update([1,3,4,m2,5])
        self.assertFalse(m._locked)
        m.lock()
        self.assertTrue(m._locked)
        self.assertFalse(m.called)
        m2.callback(10)
        self.assertTrue(m.called)
        self.assertEqual(m.result,[1,3,4,10,5])
        