import sys
import os

from djpcms.utils import test
from djpcms.utils.structures import OrderedDict

if sys.version_info < (2,7):

    class TestOrderedDict(test.TestCase):
    
        def testInstance(self):
            d = OrderedDict()
            self.assertTrue(isinstance(d,dict))
            
        def testOrderSimple(self):
            d = OrderedDict()
            d['ciao']  = 1
            d['abcbd'] = 2
            d[56]      = 3
            for n,kv in enumerate(d.iteritems(), start = 1):
                self.assertEqual(n,kv[1]) 
        
        @test.skipUnless(os.environ['stdcms'], "Requires stdcms installed")
        def testOrderList(self):
            from stdnet.utils.populate import populate
            x = populate('string',300, min = 5, max = 15)
            y = populate('string',300, min = 5, max = 15)
            data = zip(x,y)
            od = OrderedDict(data)
            self.assertEqual(len(od),300)
            for t,v in zip(od.iteritems(),data):
                self.assertEqual(t,v)
