import sys
import os
import unittest as test

from djpcms.style import *
        

class Tvariable(object):
    
    def make(self):
        raise NotImplementedError()
    
    def testEqual(self):
        a = self.make()
        self.assertEqual(a,a)
        
    def testNotEqual(self):
        a = self.make()
        b = Variable('bla')
        self.assertNotEqual(a,b)
        self.assertNotEqual(a,56)
        
    def testLessThenError(self):
        a = self.make()
        self.assertFalse(a<a)
    
    def testImmutable(self):
        a = self.make()
        self.assertRaises(AttributeError, self.set_value, a)
        
    def set_value(self, a):
        a.value = 5
    

class TestSymbol(test.TestCase):
    
    def testUnit(self):
        a = Variable('left')
        self.assertNotEqual(a.unit,a.unit)
        self.assertEqual(a.value,'left')
        
    def testNotEqual(self):
        a = Variable('left')
        b = Variable('bla')
        self.assertNotEqual(a,a)
        self.assertNotEqual(a,b)
    
    
class TestSize(Tvariable,test.TestCase):
    
    def make(self):
        return px(18)
    
    def testPX(self):
        a = px(14)
        self.assertEqual(str(a),'14px')
        self.assertEqual(a.value,14)
        self.assertEqual(str(a+2),'16px')
        self.assertEqual(str(a),'14px')
        self.assertRaises(ValueError, px, 'cjhbc')
        
    def testPC(self):
        a = pc(80)
        self.assertEqual(str(a),'80%')
        
    def testEM(self):
        a = em(1.2)
        self.assertEqual(str(a),'1.2em')
        
    def testSetError(self):
        a = px(14)
        self.assertRaises(AttributeError, self.set_value, a)
        a = em(1.8)
        self.assertRaises(AttributeError, self.set_value, a)
        a = pc(90)
        self.assertRaises(AttributeError, self.set_value, a)
        
    def testMultiply(self):
        a = px(15)
        b = 2*a
        self.assertEqual(b.unit,'px')
        self.assertEqual(b.value,30)
        self.assertEqual(str(b),'30px')
        b = 1.5*a
        self.assertEqual(b.unit,'px')
        self.assertEqual(b.value,22.5)
        self.assertEqual(str(b),'22.5px')
        self.assertRaises(TypeError,lambda: a*b)
        
    def testDivide(self):
        a = px(15)
        b = a/2
        self.assertEqual(b.unit,'px')
        self.assertEqual(b.value,7.5)
        self.assertEqual(str(b),'7.5px')
        b = a/3
        self.assertEqual(b.unit,'px')
        self.assertEqual(b.value,5)
        self.assertEqual(str(b),'5px')
        self.assertRaises(TypeError,lambda: a/b)
        

class TestSpacing(Tvariable,test.TestCase):
    
    def make(self):
        return spacing(px(5),px(2),px(10))
    
    def testSimple(self):
        a = spacing(px(5))
        self.assertEqual(a.top, px(5))
        self.assertEqual(a.right, px(5))
        self.assertEqual(a.bottom, px(5))
        self.assertEqual(a.left, px(5))
        self.assertEqual(str(a), '5px')
        self.assertEqual(a.unit,'px')
        a = spacing(px(5),px(2))
        self.assertEqual(a.top, px(5))
        self.assertEqual(a.right, px(2))
        self.assertEqual(a.bottom, px(5))
        self.assertEqual(a.left, px(2))
        self.assertEqual(str(a), '5px 2px')
        a = spacing(px(5),px(2),px(10))
        self.assertEqual(str(a.top),'5px')
        self.assertEqual(str(a.right),'2px')
        self.assertEqual(str(a.bottom),'10px')
        self.assertEqual(str(a.left),'2px')
        self.assertEqual(str(a),'5px 2px 10px')
        a = spacing(px(5),px(2),px(10),px(7))
        self.assertEqual(a.top,px(5))
        self.assertEqual(a.right,px(2))
        self.assertEqual(a.bottom,px(10))
        self.assertEqual(a.left,px(7))
        self.assertEqual(str(a),'5px 2px 10px 7px')
        
    def testMixAndMatch(self):
        a = spacing(5)
        self.assertEqual(a.top, px(5))
        self.assertEqual(a.right, px(5))
        self.assertEqual(a.bottom, px(5))
        self.assertEqual(a.left, px(5))
        self.assertEqual(str(a),'5px')
        a = spacing(5,4)
        self.assertEqual(a.top, px(5))
        self.assertEqual(a.right, px(4))
        self.assertEqual(a.bottom, px(5))
        self.assertEqual(a.left, px(4))
        self.assertEqual(str(a),'5px 4px')
        # mix and match
        a = spacing(5, em(1.1), pc(2), px(2))
        self.assertEqual(a.top,px(5))
        self.assertEqual(a.right,em(1.1))
        self.assertEqual(a.bottom,pc(2))
        self.assertEqual(str(a.left),'2px')
        self.assertEqual(str(a),'5px 1.1em 2% 2px')
        
    def testBadSpacing(self):
        self.assertRaises(ValueError, spacing, 5,4,5,6,7)
        self.assertRaises(ValueError, spacing, 5, 'bla')
        self.assertRaises(TypeError, spacing, 5, None)
        
    def testLazy(self):
        sp = spacing(lazy(lambda : 5))
        self.assertEqual(str(sp),'5px')
        
    def testVariable(self):
        # Create a named variable
        v = Variables()
        v.bla = px(5)
        # build a spacing from the named variable
        sp = spacing(v.bla)
        self.assertEqual(str(sp),'5px')
        self.assertEqual(len(sp),1)
        self.assertEqual(sp.top,px(5))
        #
        v.foo = spacing(10)
        sp = spacing(v.foo)
        self.assertEqual(str(sp),'10px')
        

class TestLazy(test.TestCase):
    
    def testError(self):
        self.assertRaises(TypeError, lazy, 5)
        self.assertRaises(TypeError, lazy, 5, 7, bla = 8)
        
    def testMeta(self):
        l = lazy(lambda : 5)
        self.assertEqual(l.value,5)
        self.assertEqual(l.unit,None)
        self.assertEqual(l.tocss(),5)
        self.assertEqual(str(l),'5')
        
        
class TestVariables(test.TestCase):
        
    def testNamespace(self):
        v = Variables()
        v.bla.margin = px(14)
        bla = v.bla
        self.assertTrue(isinstance(bla,Variables))
        self.assertEqual(bla, v.bla)
        self.assertEqual(bla._parent,v)
        
    def testNestednamespace(self):
        v = Variables()
        v.bla.default.color = '#222'
        bla = v.bla
        self.assertTrue(isinstance(bla,Variables))
        self.assertEqual(bla, v.bla)
        self.assertEqual(bla._parent,v)
        
    def testNotAssigned(self):
        v = Variables()
        bla = v.bla
        self.assertTrue(isinstance(bla, Variables))
        self.assertNotEqual(bla,v.bla)
        self.assertEqual(bla._parent,v)
    
    def testUnit(self):
        cssv = Variables()
        cssv.bla = px(14)
        bla = cssv.bla
        self.assertEqual(bla.unit,'px')
    
    
class TestRGBA(test.TestCase):
    
    def testRGBA(self):
        c = RGBA(34.67,156.98,245.1)
        self.assertEqual(c,(35,157,245,1))
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
        self.assertEqual(c.alpha,1)
        self.assertEqual(c.value,(240,248,255,1))
        self.assertEqual(str(c),'#f0f8ff')
        
    def testOpacity(self):
        c = color('f0f8ff',0.7)
        self.assertEqual(c.alpha,0.7)
        self.assertEqual(c.value,(240,248,255,0.7))
        self.assertEqual(str(c),'rgba(240, 248, 255, 0.7)')
        
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
        c = color((-1,145,145,0.7))
        self.assertEqual(c.alpha,0.7)
        self.assertEqual(c.value,(0,145,145,0.7))
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
        c3 = color.mix(c1,c2)
        self.assertEqual(c3.alpha,c1.alpha)
        l1 = color.lighten(c1, 10)
        self.assertEqual(c1.value, color.darken(l1, 10))


class TestVariable(test.TestCase):
    
    def testPyValue(self):
        self.assertEqual(Variable.pyvalue(cssv.cscdcsdcdcs),None)
        self.assertEqual(Variable.pyvalue(lambda: 5),5)
        
    
class TestCSS(test.TestCase):
    
    def testSimple(self):
        # the variable does not exist
        c = css('#random', margin = cssv.skjncdfcd)
        self.assertFalse(c._attributes)
    
    def testError(self):
        self.assertRaises(TypeError, css, '.foo', [])
        
    
class TestMixins(test.TestCase):
    
    def testNotImplemented(self):
        m = mixin()
        self.assertRaises(NotImplementedError,lambda: m(None))
        
    def test_clearfix(self):
        s = css('.bla',
                clearfix(),
                display = 'block')
        elems = list(s)
        self.assertEqual(len(elems),3)
        text = str(s)
        self.assertTrue('*zoom: 1;' in text)
        self.assertEqual(text,\
'''.bla {
    display: block;
    *zoom: 1;
}

.bla:before,
.bla:after {
    content: "";
    display: table;
}

.bla:after {
    clear: both;
}''')
        
    def testRadius(self):
        r = px(5)
        s = css('.bla', radius(r))
        self.assertEqual(str(s),\
'''.bla {
    -webkit-border-radius: 5px;
       -moz-border-radius: 5px;
            border-radius: 5px;
}''')
        
    def testBoxShadow(self):
        s = css('.bla',
                shadow('10px 10px 5px #888'),
                display = 'block')
        r = '''
    -webkit-box-shadow: 10px 10px 5px #888;
       -moz-box-shadow: 10px 10px 5px #888;
            box-shadow: 10px 10px 5px #888;'''
        self.assertTrue(r in str(s))
    
    def test_fixtop(self):
        s = css('.foo',
                fixtop(3000))
        self.assertTrue(s.mixins)
        r = '''
    left: 0;
    top: 0;
    right: 0;
    position: fixed;
    z-index: 3000;'''
        self.assertTrue(r in str(s))
        
    def test_clickable(self):
        s = css('.click',
                clickable())
        self.assertEqual(str(s),'.click {\n}')
        s = css('.click', clickable(default = bcd(color = color('#333'))))
        self.assertEqual(str(s),'.click {\n    color: #333333;\n}')
        s = css('.click', clickable(default = bcd(color = '#333333'),
                                    hover = bcd(color = '#000000'),
                                    active = bcd(color = '#222222')))
        self.assertEqual(str(s),'''.click {
    color: #333333;
}

.click:hover {
    color: #000000;
}

.click.active {
    color: #222222;
}''')
        

class TestGradient(test.TestCase):
    
    def test_vgradient(self):
        s = css('.bla',
                gradient(('v','#ffffff','#f5f5f5')),
                display = 'block')
        self.assertTrue(s.mixins)
        r = '''
    background-color: #f5f5f5;
    background-image: -moz-linear-gradient(top, #ffffff, #f5f5f5);
    background-image: -ms-linear-gradient(top, #ffffff, #f5f5f5);
    background-image: -webkit-gradient(linear, 0 0, 0 100%, from(#ffffff), to(#f5f5f5));
    background-image: -webkit-linear-gradient(top, #ffffff, #f5f5f5);
    background-image: -o-linear-gradient(top, #ffffff, #f5f5f5);
    background-image: linear-gradient(top, #ffffff, #f5f5f5);
    background-repeat: repeat-x;
    filter: progid:DXImageTransform.Microsoft.gradient(startColorstr='#ffffff', endColorstr='#f5f5f5', GradientType=0);'''
        self.assertTrue(r in str(s))
    
    def testColor(self):
        d = {}
        g = gradient('#222')
        g(d)
        self.assertEqual(d['background'],color('#222'))
            
    def testBadGradient(self):
        d = {}
        self.assertRaises(ValueError, lambda: gradient(5)(d))
        self.assertRaises(ValueError, lambda: gradient((5,))(d))
        self.assertRaises(ValueError, lambda: gradient((5,4))(d))
        self.assertRaises(ValueError, lambda: gradient((4,5,6,7))(d))
        
        
class TestGrid(test.TestCase):
    
    def test_grid940(self):
        g = grid(12,60,20)
        self.assertTrue(g.id)
        self.assertEqual(g.columns,12)
        self.assertEqual(g.width,940)
        elements = tuple(g())
        self.assertEqual(len(elements),15)
        
    def testTemplate(self):
        c = css('div.test', color = '#333')
        self.assertEqual(c.tag, 'div.test')
        text = str(c)
        self.assertTrue('color: #333;' in text)
        
    
class TestNavigation(test.TestCase):
    
    def testMeta(self):
        nav = horizontal_navigation()
        self.assertEqual(nav.float,'left')
        nav = horizontal_navigation(float=  'bla')
        self.assertEqual(nav.float,'left')
        nav = horizontal_navigation(float=  'right')
        self.assertEqual(nav.float,'right')
        
    def testRender(self):
        nav = css('.nav', horizontal_navigation())
        text = str(nav)
        self.assertTrue(text)
        
        
class TestTopBar(test.TestCase):
    
    def test_meta(self):
        from style.elements import topbar
        tb = css('.topbar', topbar.topbar())
        text = str(tb)
        self.assertTrue(text)
        
        
class TestScript(test.TestCase):
    
    def testArgParser(self):
        parser = add_arguments()
        self.assertTrue(parser)
        
    def testRender(self):
        # for coverage
        main(argv = ['-v'], verbose = False)
        # dump css file
        main(argv = ['-o','pytest.css'], verbose = False)
        f = open('pytest.css')
        data = f.read()
        f.close()
        os.remove('pytest.css')
        self.assertTrue(data)
        self.assertTrue('''
body {
    font-size: 14px;
    color: #222222;
    text-align: left;
    background: #ffffff;
    min-width: 960px;
    line-height: 18px;
    font-family: Helvetica,Arial,'Liberation Sans',FreeSans,sans-serif;
}''' in data)
    
    
if __name__ == '__main__':
    try:
        import nose
    except ImportError:
        test.main()
    else:
        nose.main()
    
    