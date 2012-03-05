from djpcms.utils import test
from djpcms.style import color


class TestColor(test.TestCase):
    
    def testSimple(self):
        c = color('f0f8ff')
        self.assertEqual(c.alpha,1)
        self.assertEqual(c.rgb,(240,248,255))
        
    def testHSL(self):
        c = color('f0f8ff')
        v = c.tohsl()
        self.assertEqual(v['a'],1)
        self.assertAlmostEqual(v['h'],208)
        self.assertAlmostEqual(v['s'],1.0)
        self.assertAlmostEqual(round(v['l'],3),0.971)