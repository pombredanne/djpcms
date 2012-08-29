import sys
import os
import json

from djpcms.media.style import *
from djpcms.utils import test

from .vars import TestStyling
        

class TestCSS(TestStyling):
    
    def testBody(self):
        body = css('body')
        self.assertTrue(body.is_body)
        self.assertEqual(body, css.body())
        
    def testClone(self):
        body = css.body().clone()
        self.assertTrue(body._clone)
        def test_children(elem):
            self.assertTrue(elem._clone)
            self.assertTrue(isinstance(elem, css))
            for cl in elem.children.values():
                self.assertTrue(cl)
                for child in cl:
                    test_children(child)                    
        test_children(body)
        
    def testSimple(self):
        # the variable does not exist
        c = css('#random', margin=cssv.skjncdfcd)
        self.assertFalse(c.attributes)
        self.assertEqual(c.parent, css('body'))
        
    
class TestMixins(TestStyling):
    '''Test the simple mixins'''
    def testNotImplemented(self):
        m = mixin()
        self.assertRaises(NotImplementedError,lambda: m(None))
        
    def test_clearfix(self):
        s = css('.bla',
                clearfix(),
                display='block')
        text = s.render()
        self.assertTrue('*zoom: 1;' in text)
        self.assertEqual(text,\
'''.bla {
    display: block;
    *zoom: 1;
}

.bla:before {
    content: "";
    display: table;
}

.bla:after {
    content: "";
    display: table;
    clear: both;
}
''')
        
    def testRadius(self):
        r = px(5)
        s = css('.bla', radius(r))
        text = s.render()
        self.assertEqual(text,\
'''.bla {
    -webkit-border-radius: 5px;
       -moz-border-radius: 5px;
            border-radius: 5px;
}
''')
    
    def testRadiusSpacing(self):
        ra = radius(spacing(px(5),0))
        s = css('.bla', ra)
        text = s.render()
        self.assertEqual(text,\
'''.bla {
    -webkit-border-radius: 5px 0;
       -moz-border-radius: 5px 0;
            border-radius: 5px 0;
}
''')
    
    def testRadiusVariable(self):
        r = Variable(spacing(px(5),0))
        ra = radius(r)
        s = css('.bla', ra)
        text = s.render()
        self.assertEqual(text,\
'''.bla {
    -webkit-border-radius: 5px 0;
       -moz-border-radius: 5px 0;
            border-radius: 5px 0;
}
''')
    
    def testBorder(self):
        b = border(color='#555')
        self.assertEqual(b.color, '#555')
        s = css('.bla', b)
        text = s.render()
        self.assertEqual(text,\
'''.bla {
    border: 1px solid #555555;
}
''')
    
    def testBorderVariables(self):
        c = Variables()
        c.border.color = '#222'
        c.border.style = 'dotted'
        c.border.width = None
        b = border(**c.border.params())
        s = css('.bla', b)
        text = s.render()
        self.assertEqual(text,\
'''.bla {
    border: 1px dotted #222;
}
''')
        
    def testBorderVariables2(self):
        c = Variables()
        c.border.color = color('222')
        c.border.style = 'dotted'
        c.border.width = None
        b = border(**c.border.params())
        s = css('.bla', b)
        text = s.render()
        self.assertEqual(text,\
'''.bla {
    border: 1px dotted #222222;
}
''')
            
    def testBoxShadow(self):
        s = css('.bla',
                shadow('10px 10px 5px #888'),
                display = 'block')
        text = s.render()
        r = '''
    -webkit-box-shadow: 10px 10px 5px #888;
       -moz-box-shadow: 10px 10px 5px #888;
            box-shadow: 10px 10px 5px #888;'''
        self.assertTrue(r in text)
    
    def test_fixtop(self):
        s = css('.foo',
                fixtop(3000))
        text = s.render()
        r = '''
    left: 0;
    top: 0;
    right: 0;
    position: fixed;
    z-index: 3000;'''
        self.assertTrue(r in text)
        
    def test_clickable(self):
        s = css('.click',
                clickable(cursor=None))
        self.assertEqual(s.render(),'')
        s = css('.click', clickable(default = bcd(color = color('#333'))))
        self.assertEqual(s.render(),'''.click {
    cursor: pointer;
    color: #333333;
}
''')
        s = css('.click', clickable(default=bcd(color='#333333'),
                                    hover=bcd(color='#000000'),
                                    active=bcd(color='#222222')))
        text = s.render()
        self.assertEqual(text, '''.click {
    cursor: pointer;
    color: #333333;
}

.click:hover {
    color: #000000;
}

.click.ui-state-hover {
    color: #000000;
}

.click:active {
    color: #222222;
}

.click.ui-state-active {
    color: #222222;
}
''')
        

class TestGradient(TestStyling):
    
    def test_vgradient(self):
        s = css('.bla',
                gradient(('v','#ffffff','#f5f5f5')),
                display = 'block')
        text = s.render()
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
        self.assertTrue(r in text)
    
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
        
        
class TestGrid(TestStyling):
    
    def test_grid940(self):
        g = grid(12,60,20)
        elem = css.make('body')
        self.assertEqual(g.columns, 12)
        self.assertEqual(g.width, 940)
        g(elem)
        self.assertEqual(len(elem._children),2)
        
    def testTemplate(self):
        c = css('div.test', color = '#333')
        self.assertEqual(c.tag, 'div.test')
        text = c.render()
        self.assertTrue('color: #333;' in text)
        
    
class TestBCD(TestStyling):
    
    def testObject(self):
        b = bcd()
        self.assertFalse(b.color)
        self.assertFalse(b.text_decoration)
        self.assertFalse(b.text_shadow)
        
    def testCss(self):
        c = css('#testbcd', bcd(color='#444'))
        self.assertTrue(c.children)
        text = c.render()
        self.assertEqual(text,\
'''#testbcd {
    color: #444444;
}
''')

    
class TestNavigation(TestStyling):
    
    def testMeta(self):
        nav = horizontal_navigation()
        self.assertEqual(nav.float, 'left')
        nav = horizontal_navigation(float='bla')
        self.assertEqual(nav.float, 'left')
        nav = horizontal_navigation(float='right')
        self.assertEqual(nav.float, 'right')
        
    def testRender(self):
        nav = css('.nav', horizontal_navigation())
        text = nav.render()
        self.assertTrue(text)
        
        
class TestTopBar(TestStyling):
    
    def test_meta(self):
        from djpcms.apps.nav.style import topbar
        tb = css('.topbar', topbar())
        text = tb.render()
        self.assertTrue(text)
        

class TestUi(TestStyling):
    
    def testDefinitionList(self):
        from djpcms.html import classes
        dl = css.body().children['.%s' % classes.object_definition]
        self.assertEqual(len(dl), 1)
        dl = dl[0]
        text = dl.render()
        self.assertTrue('.%s dl' % classes.object_definition in text)
    
class TestScript(TestStyling):
    
    def testVariables(self):
        # for coverage
        stream = dump_theme(dump_variables=True)
        self.assertTrue(stream)
        vars = json.loads(stream)
        self.assertTrue(vars)
        
    def testRender(self):
        stream = dump_theme()
        self.assertTrue(stream)
        self.assertTrue('''
body {
    font-size: 14px;
    color: #444444;
    text-align: left;
    height: 100%;
    min-width: 960px;
    line-height: 18px;
    font-family: Helvetica,Arial,'Liberation Sans',FreeSans,sans-serif;
    background: #ffffff;
}''' in stream)

    
    