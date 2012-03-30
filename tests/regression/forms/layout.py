from djpcms import forms
from djpcms.html.layout import grid
from djpcms.forms import layout
from djpcms.apps.contentedit import HtmlPageForm
from djpcms.utils import test


class TestFormLayout(test.TestCase):
    
    def testColumns(self):
        c = layout.Columns('field1','field2')
        self.assertEqual(c.grid, grid('grid 50-50'))
        # test error
        self.assertRaises(ValueError, layout.Columns, 'field1',
                          grid = grid('grid 33-33-33'))
        
    def testHtmlPageForm(self):
        l = HtmlPageForm.layout
        self.assertTrue(l)
        # the columns are the second child (firs is the message hoder)
        columns = l.allchildren[1]
        self.assertEqual(columns.grid, grid('grid 33-33-33'))