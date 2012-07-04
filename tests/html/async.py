from djpcms import html
from djpcms.utils.async import Deferred, is_async
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