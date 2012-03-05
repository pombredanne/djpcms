from djpcms.utils import test
from djpcms.style import css, grid
from djpcms.core.management.commands.style import Command


class TestCss(test.TestCase):
    
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
        
    def testBox(self):
        box = css.get('.djpcms-html-box')[0]
        self.assertEqual(box.tag,'.djpcms-html-box')
        html = str(box)