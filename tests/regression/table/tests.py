from py2py3 import zip

from djpcms import test, forms, html, to_string


class TableTests(test.TestCase):
    
    def testSimple(self):
        tbl = html.Table(['first','second'])
        self.assertTrue(tbl.internal['headers'])
        ht = tbl.render()
        self.assertTrue('<table>' in ht)
        self.assertTrue('</table>' in ht)
        self.assertTrue('<thead>' in ht)
        self.assertTrue('</thead>' in ht)
        self.assertTrue('<tbody>' in ht)
        self.assertTrue('</tbody>' in ht)
        self.assertTrue('<tfoot>' in ht)
        self.assertTrue('</tfoot>' in ht)
        
    def testSimpleNoFooter(self):
        tbl = html.Table(['first','second'], footer = False)
        ht = tbl.render()
        self.assertTrue('<table>' in ht)
        self.assertTrue('</table>' in ht)
        self.assertTrue('<thead>' in ht)
        self.assertTrue('</thead>' in ht)
        self.assertTrue('<tbody>' in ht)
        self.assertTrue('</tbody>' in ht)
        self.assertFalse('<tfoot>' in ht)
        self.assertFalse('</tfoot>' in ht)
        
    def testTableWithData(self):
        data = zip(('pippo','pluto','luna'),(3,4,1))
        tbl = html.Table(['first','second'], data)
        ht = tbl.render()
        self.assertTrue('<td>pippo</td><td>3</td>' in ht)
        
    