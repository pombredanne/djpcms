from djpcms import html
from djpcms.utils import test


class TestDomTree(test.TestCase):
    
    def testSimple(self):
        a = html.Widget('div')
        self.assertEqual(a.parent, None)
        a.add(html.Widget('div', cn='child'))
        self.assertEqual(a.parent, None)
        self.assertEqual(len(a),1)
        for c in a:
            self.assertEqual(c.parent,a)
            self.assertEqual(c.root,a)