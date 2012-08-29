from djpcms.media.style import *
from djpcms.utils import test


class TestStyling(test.TestCase):
    
    def get_original(self):
        return set(css.body().all_css_children())
        
    def setUp(self):
        import djpcms.apps.page.style
        import djpcms.apps.color.style
        import djpcms.apps.contentedit.style
        import djpcms.apps.fontawesome.style
        import djpcms.apps.nav.style
        import djpcms.apps.ui.style
        self.original = self.get_original()
        self.cssv = Variables()
        
    def tearDown(self):
        for c in list(css.body().all_css_children()):
            if c not in self.original:
                c.destroy()
        self.assertEqual(self.original, self.get_original())


class TestLazy(test.TestCase):
    
    def testError(self):
        self.assertRaises(TypeError, lazy, 5)
        self.assertRaises(TypeError, lazy, 5, 7, bla=8)
        
    def testMeta(self):
        l = lazy(lambda : 5)
        self.assertEqual(l.value,5)
        self.assertEqual(l.unit,None)
        self.assertEqual(l.tocss(),5)
        self.assertEqual(str(l),'5')
        
        
class TestVariables(TestStyling):
    
    def testPyValue(self):
        self.assertEqual(Variable.pyvalue(cssv.cscdcsdcdcs),None)
        self.assertEqual(Variable.pyvalue(lambda: 5),5)
        
    def testNamedVariable(self):
        cssv = self.cssv
        cssv.bla = 5
        self.assertEqual(cssv.bla.value, 5)
        self.assertEqual(cssv.bla.name, 'bla')
        # Assign a variable to a variable
        cssv.foo = cssv.bla
        self.assertEqual(cssv.foo.name, 'foo')
        self.assertEqual(cssv.foo.value, 5)
        # Override value in bla
        cssv.bla = 4
        self.assertEqual(cssv.bla.value, 4)
        self.assertEqual(cssv.foo.value, 4)
        # Override foo
        cssv.foo = 8
        self.assertEqual(cssv.bla.value, 4)
        self.assertEqual(cssv.foo.value, 8)
        
    def testTheme(self):
        cssv = self.cssv
        cssv.bla = 5
        cssv.foo = cssv.bla
        with cssv.theme('mare') as t:
            t.bla = 8
            self.assertEqual(cssv.bla.value, 8)
            self.assertEqual(cssv.foo.value, 8)
        self.assertEqual(cssv.bla.value, 5)
        self.assertEqual(cssv.foo.value, 5)
        
    def testNamespace(self):
        v = self.cssv
        v.bla.margin = px(14)
        bla = v.bla
        self.assertTrue(isinstance(bla,Variables))
        self.assertEqual(bla, v.bla)
        self.assertEqual(bla.parent, v)
        
    def testCopyVarables(self):
        v = self.cssv
        v.bla.default.color = '#222'
        v.bla.default.background = '#444'
        v.bla.hover.background = '#111'
        v.foo = v.bla.copy()
        self.assertEqual(str(v.foo.default.color), '#222')
        # No change the value of the original variable
        v.bla.default.color = '#333'
        self.assertEqual(str(v.foo.default.color), '#333')
        self.assertEqual(str(v.bla.default.color), '#333')
        # Now override value
        v.foo.default.color = '#777'
        self.assertEqual(str(v.foo.default.color), '#777')
        self.assertEqual(str(v.bla.default.color), '#333')
        
    def testNestednamespace(self):
        v = self.cssv
        v.bla.default.color = '#222'
        bla = v.bla
        self.assertTrue(isinstance(bla,Variables))
        self.assertEqual(bla, v.bla)
        self.assertEqual(bla.parent, v)
        
    def testNotAssigned(self):
        v = self.cssv
        bla = v.bla
        self.assertTrue(isinstance(bla, Variables))
        self.assertNotEqual(bla,v.bla)
        self.assertEqual(bla.parent, v)
    
    def testUnit(self):
        v = self.cssv
        cssv.bla = px(14)
        bla = cssv.bla
        self.assertEqual(bla.unit,'px')