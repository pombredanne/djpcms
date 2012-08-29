from djpcms.media.style import *
from djpcms.utils import test
    
    
class TestRGBA(test.TestCase):
    
    def testRGBA(self):
        c = RGBA(34.67, 156.98, 245.1)
        self.assertEqual(c, (35, 157, 245, 1))
        self.assertRaises(ValueError, lambda: c + 4)
        
    def testRGBAMeta(self):
        c = RGBA(34.67,156.98,245.1)
        v = c.clone()
        self.assertEqual(c,v)
        self.assertNotEqual(id(c),id(v))
        v = c.clone(r=0)
        self.assertNotEqual(c,v)
        self.assertEqual(v.r,0)
        
    def testRGBASubtract(self):
        c = RGBA(34.67,156.98,245.1)
        self.assertEqual(c,(35,157,245,1))
        self.assertRaises(ValueError, lambda: c + 4)
        self.assertRaises(ValueError, lambda: c - 4)
        # this should give me black c
        c = c - c
        self.assertEqual(c,(35,157,245,1))
        
    def testRGBAmixSimple(self):
        c1 = RGBA(255,255,255)
        c2 = RGBA(0,0,0)
        c3 = c1 + c2
        c4 = RGBA.mix(c1,c2)
        self.assertEqual(c3,c4)
        self.assertEqual(c3.r,128)
        self.assertEqual(c3.g,128)
        self.assertEqual(c3.b,128)
        self.assertEqual(c3.alpha,1)
        
    def testRGBAmixAlpha(self):
        c1 = RGBA(255,0,0)
        c2 = RGBA(0,255,0)
        c3 = RGBA.mix(c1,c2)
        self.assertEqual(c3.r,128)
        self.assertEqual(c3.g,128)
        self.assertEqual(c3.b,0)
        self.assertEqual(c3.alpha,1)
        #
        c1 = RGBA(255,0,0,0.5)
        c2 = RGBA(0,255,0,0.5)
        c3 = RGBA.mix(c1,c2)
        self.assertEqual(c3.r,128)
        self.assertEqual(c3.g,128)
        self.assertEqual(c3.b,0)
        self.assertEqual(c3.alpha,0.5)
        #
        c1 = RGBA(255,0,0,0.8)
        c2 = RGBA(0,255,0,0.5)
        c3 = RGBA.mix(c1,c2)
        self.assertEqual(c3.r,166)
        self.assertEqual(c3.g,89)
        self.assertEqual(c3.b,0)
        self.assertEqual(c3.alpha,0.65)
        #
        c1 = RGBA(255,0,0,0.5)
        c2 = RGBA(0,255,0,0.8)
        c3 = RGBA.mix(c1,c2)
        self.assertEqual(c3.r,89)
        self.assertEqual(c3.g,166)
        self.assertEqual(c3.b,0)
        self.assertEqual(c3.alpha,0.65)

    def testDarken(self):
        c1 = color('3366FF').value
        hsla1 = c1.tohsla()
        c2 = c1.darken(10)
        hsla2 = c2.tohsla()
        self.assertAlmostEqual(hsla1.h,hsla2.h,3)
        self.assertAlmostEqual(hsla1.s,hsla2.s)
        self.assertAlmostEqual(hsla1.l,hsla2.l+0.1)
        c3 = c2.lighten(10)
        self.assertEqual(c1,c3)
        hsla3 = c3.tohsla()
        self.assertAlmostEqual(hsla1.h,hsla3.h,3)
        self.assertAlmostEqual(hsla1.s,hsla3.s)
        self.assertAlmostEqual(hsla1.l,hsla3.l)


class TestColor(test.TestCase):
    
    def testSimple(self):
        c = color('f0f8ff')
        self.assertEqual(c.alpha, 1)
        self.assertEqual(c.value, (240, 248, 255, 1))
        self.assertEqual(str(c),'#f0f8ff')
        
    def testStr(self):
        c = color('transparent')
        self.assertEqual(c, 'transparent')
        c = color('inherit')
        self.assertEqual(c, 'inherit')
        self.assertRaises(ValueError, color, 'skjbjbc')
        
    def testOpacity(self):
        c = color('f0f8ff', 0.7)
        self.assertEqual(c.alpha, 0.7)
        self.assertEqual(c.value, (240, 248, 255, 0.7))
        self.assertEqual(str(c), 'rgba(240, 248, 255, 0.7)')
        
    def testAdd(self):
        c1 = color('000')
        c2 = color('fff')
        c = c1 + c2
        self.assertEqual(c.alpha,1)
        self.assertEqual(c.r,128)
        self.assertEqual(c.g,128)
        self.assertEqual(c.b,128)
        self.assertEqual(c.alpha,1)
        self.assertRaises(ValueError, lambda: c1 + 4)
        
    def testHSL(self):
        c = color('000')
        self.assertEqual(c.value,(0,0,0,1))
        v = c.tohsla()
        self.assertEqual(v.alpha,1)
        self.assertAlmostEqual(v.h,0)
        self.assertAlmostEqual(v.s,0)
        self.assertAlmostEqual(v.l,0)
        #
        c = color('fff')
        self.assertEqual(c.value,(255,255,255,1))
        v = c.tohsla()
        self.assertEqual(v.alpha,1)
        self.assertAlmostEqual(v.h,0)
        self.assertAlmostEqual(v.s,0)
        self.assertAlmostEqual(v.l,1)
        #
        c = color('f0f8ff')
        self.assertEqual(c.value,(240,248,255,1))
        v = c.tohsla()
        self.assertEqual(v.alpha,1)
        self.assertAlmostEqual(360*v.h,208)
        self.assertAlmostEqual(v.s,1.0)
        self.assertAlmostEqual(round(v.l,3),0.971)
        
    def testHSV(self):
        c = color('000')
        self.assertEqual(c.value,(0,0,0,1))
        v = c.tohsva()
        self.assertEqual(v.alpha,1)
        self.assertAlmostEqual(v.h,0)
        self.assertAlmostEqual(v.s,0)
        self.assertAlmostEqual(v.v,0)
        #
        c = color('fff')
        self.assertEqual(c.value,(255,255,255,1))
        v = c.tohsva()
        self.assertEqual(v.alpha,1)
        self.assertAlmostEqual(v.h,0)
        self.assertAlmostEqual(v.s,0)
        self.assertAlmostEqual(v.v,1)
        #
        c = color('f0f8ff')
        self.assertEqual(c.value,(240,248,255,1))
        v = c.tohsva()
        self.assertEqual(v.alpha,1)
        self.assertAlmostEqual(360*v.h,208)
        self.assertAlmostEqual(round(v.s,3),0.059)
        self.assertAlmostEqual(v.v,1)
        
    def testmake(self):
        # Make sure we cover RGBA.make
        c = color((-1, 145, 145, 0.7))
        self.assertEqual(c.alpha, 0.7)
        self.assertEqual(c.value, (0, 145, 145, 0.7))
        #
        c = RGBA.make('000',0.6)
        self.assertEqual(c,(0,0,0,0.6))
        c = RGBA.make(c,0.8)
        self.assertEqual(c,(0,0,0,0.8))
        #
        d = color(c)
        self.assertEqual(d.value,c)
        self.assertEqual(id(d.value),id(c))
        #
        f = color(d)
        self.assertEqual(d.value,c)
        self.assertEqual(id(d.value),id(c))
        
    def testMix(self):
        c1 = color('000')
        c2 = color('333')
        c3 = mix_colors(c1, c2)
        self.assertEqual(c3.alpha, c1.alpha)
        l1 = lighten(c1, 10)
        self.assertEqual(c1.value, darken(l1, 10))
        
    def testFromVariable(self):
        v = Variables()
        v.foo = '#fff'
        c = color(v.foo)
        self.assertEqual(id(v.foo), id(c))

