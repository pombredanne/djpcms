from djpcms.utils import test
from djpcms.style import css, shadow, gradient


class TestCss(test.TestCase):
    
    def testBoxShadow(self):
        s = shadow(css('.bla', display = 'block'),
                   '10px 10px 5px #888').css()
        self.assertTrue(len(s),1)
        s = s[0]
        r = '''
    -webkit-box-shadow: 10px 10px 5px #888;
       -moz-box-shadow: 10px 10px 5px #888;
            box-shadow: 10px 10px 5px #888;'''
        self.assertTrue(r in str(s))
        
    def test_vgradient(self):
        s = gradient(css('.bla', display = 'block'),
                     ('v','#ffffff','#f5f5f5')).css()
        self.assertTrue(len(s),1)
        s = s[0]
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
        