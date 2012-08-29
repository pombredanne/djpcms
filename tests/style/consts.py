from djpcms.media.style import *
from djpcms.utils import test


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
        self.assertNotEqual(a.unit, a.unit)
        self.assertEqual(a.value,'left')
        
    def testNotEqual(self):
        a = Variable('left')
        b = Variable('bla')
        self.assertNotEqual(a, a)
        self.assertNotEqual(a, b)
    
    
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
        self.assertEqual(b.value,22)
        self.assertEqual(str(b),'22px')
        self.assertRaises(TypeError,lambda: a*b)
        
    def testDivide(self):
        a = px(15)
        b = a/2
        self.assertEqual(b.unit, 'px')
        self.assertEqual(b.value, 7)
        self.assertEqual(str(b), '7px')
        b = a/3
        self.assertEqual(b.unit,'px')
        self.assertEqual(b.value,5)
        self.assertEqual(str(b),'5px')
        self.assertRaises(TypeError,lambda: a/b)
        
    def testVariable(self):
        v = Variables()
        v.size = px(5)
        self.assertEqual(str(v.size), '5px')
        self.assertEqual(px(v.size), v.size)
        

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
        sp = spacing(5, None)
        self.assertEqual(str(sp), '5px')
        
    def testLazy(self):
        sp = lazy(lambda : spacing(5))
        self.assertEqual(str(sp),'5px')
        
    def testVariable(self):
        # Create a named variable
        v = Variables()
        #
        v.bla = px(5)
        sp = spacing(v.bla)
        self.assertEqual(sp, v.bla)
        self.assertEqual(sp.top, px(5))
        self.assertEqual(str(sp), '5px')
        #
        v.foo = 5
        sp = spacing(v.foo)
        # Not equal because there is no unit
        self.assertNotEqual(sp, v.foo)
        self.assertEqual(id(sp), id(v.foo))
        self.assertRaises(AttributeError, lambda: sp.top)
        self.assertEqual(str(sp), '5')
        
    def testBadVariable(self):
        v = Variables()
        v.bla = spacing(5, 4)
        sp = spacing(v.bla, px(3))
        self.assertEqual(sp.top, v.bla)
        self.assertEqual(sp.bottom, v.bla)
        self.assertRaises(TypeError, sp.tocss)
        
    def testMultiply(self):
        a = spacing(5, 10)
        b = 0.5*a
        self.assertEqual(b.left, 0.5*a.left);