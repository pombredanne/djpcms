from djpcms import html
from djpcms.utils.async import Deferred, is_async
from djpcms.utils.httpurl import chr, to_bytes
from djpcms.utils import test

w = html.Widget


class TestInputs(test.TestCase):
    
    def testSimple(self):
        s = Deferred()
        elem = w('div', s)
        self.assertEqual(len(elem), 1)
        text = elem.render()
        self.assertTrue(is_async(text))
        self.assertFalse(text.called)
        s.callback('ciao')
        self.assertTrue(text.called)
        text = text.result
        self.assertEqual(text,'<div>ciao</div>')
        
    def testNone(self):
        s = Deferred()
        elem = w('div', s)
        text = elem.render()
        self.assertFalse(text.called)
        s.callback(None)
        self.assertTrue(text.called)
        text = text.result
        self.assertEqual(text,'<div></div>')
        
    def testbytes(self):
        s = Deferred()
        elem = w('div', s)
        text = elem.render()
        self.assertFalse(text.called)
        uv = chr(678) + chr(679)
        c = to_bytes(uv)
        s.callback(c)
        self.assertTrue(text.called)
        text = text.result
        self.assertEqual(text, '<div>%s</div>' % uv)
        
    def testNotString(self):
        s = Deferred()
        elem = w('div', s)
        text = elem.render()
        self.assertFalse(text.called)
        s.callback(2000)
        self.assertTrue(text.called)
        text = text.result
        self.assertEqual(text, '<div>2000</div>')