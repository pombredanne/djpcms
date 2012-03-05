from djpcms.utils import test
from djpcms.style import css, shadow, gradient, clearfix


class TestCss(test.TestCase):
    
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
        
    def testBoxShadow(self):
        s = css('.bla',
                shadow('10px 10px 5px #888'),
                display = 'block')
        r = '''
    -webkit-box-shadow: 10px 10px 5px #888;
       -moz-box-shadow: 10px 10px 5px #888;
            box-shadow: 10px 10px 5px #888;'''
        self.assertTrue(r in str(s))
        
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
        