from djpcms.utils import test
from djpcms.utils.async import Deferred, Failure, MultiDeferred

def async_pair(d = None):
    if d is None:
        d = Deferred()
    r = Deferred()
    d.add_callback(r.callback)
    return d, r
    
def raise_excetion(resul):
    raise Exception("I'm an exception")

class Cbk(Deferred):
    '''A deferred object'''
    def __init__(self, r = None):
        super(Cbk,self).__init__()
        if r is not None:
            self.r = (r,)
        else:
            self.r = ()
            
    def add(self, result):
        self.r += (result,)
        return self
        
    def set_result(self, result):
        self.add(result)
        self.callback(self.r)
    
    def set_error(self):
        try:
            raise ValueError('Bad callback')
        except Exception as e:
            self.callback(e)


class TestDeferred(test.TestCase):
    
    def testSimple(self):
        d = Deferred()
        self.assertFalse(d.called)
        self.assertFalse(d.running)
        self.assertEqual(str(d),'Deferred')
        d.callback('ciao')
        self.assertTrue(d.called)
        self.assertEqual(d.result,'ciao')
        self.assertRaises(RuntimeError, d.callback,'bla')
        
    def testWrongOperations(self):
        d = Deferred()
        self.assertRaises(RuntimeError, d.callback, Deferred())

    def testCallbacks(self):
        d, cbk = async_pair()
        self.assertFalse(d.called)
        d.callback('ciao')
        self.assertTrue(d.called)
        self.assertEqual(cbk.result,'ciao')
        
    def testError(self):
        d, cbk = async_pair()
        d.add_callback(raise_excetion)
        self.assertFalse(d.called)
        d.callback('ciao')
        self.assertTrue(d.called)
        self.assertTrue(isinstance(d.result, Failure))
        self.assertTrue(str(d.result))
        self.assertRaises(Exception, d.result.raise_error)
        
    def testDeferredCallback(self):
        d = Deferred()
        d.add_callback(lambda r : Cbk(r))
        self.assertFalse(d.called)
        result = d.callback('ciao')
        self.assertTrue(d.called)
        self.assertEqual(d.paused,1)
        self.assertEqual(len(result._callbacks),1)
        self.assertFalse(result.called)
        result.set_result('luca')
        self.assertTrue(result.called)
        self.assertEqual(result.result,('ciao','luca'))
        self.assertEqual(d.paused,0)
        
        
class TestMultiDeferred(test.TestCase):
    
    def testSimple(self):
        d = MultiDeferred()
        self.assertFalse(d.called)
        self.assertFalse(d._locked)
        self.assertFalse(d._underlyings)
        self.assertFalse(d._results)
        d.lock()
        self.assertTrue(d.called)
        self.assertTrue(d._locked)
        self.assertEqual(d.result,[])
        self.assertRaises(RuntimeError, d.lock)
        self.assertRaises(RuntimeError, d._finish)
        
    def testMulti(self):
        d = MultiDeferred()
        d1 = Deferred()
        d2 = Deferred()
        d.add(d1)
        d.add(d2)
        self.assertRaises(ValueError, d.add, 'bla')
        self.assertRaises(RuntimeError, d._finish)
        d.lock()
        self.assertRaises(RuntimeError, d._finish)
        self.assertRaises(RuntimeError, d.lock)
        self.assertRaises(RuntimeError, d.add, d1)
        self.assertFalse(d.called)
        d2.callback('first')
        self.assertFalse(d.called)
        d1.callback('second')
        self.assertTrue(d.called)
        self.assertEqual(d.result,['second','first'])
        
    def testUpdate(self):
        d1 = Deferred()
        d2 = Deferred()
        d = MultiDeferred()
        d.update((d1,d2)).lock()
        d1.callback('first')
        d2.callback('second')
        self.assertTrue(d.called)
        self.assertEqual(d.result,['first','second'])
    
    
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
        