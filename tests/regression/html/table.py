from djpcms.utils import test, zip
from djpcms import forms, html, to_string


class TableTests(test.TestCase):
    heads = ('first','second')
    
    def pagination(self, **kwargs):
        pag = html.Pagination(self.heads, **kwargs)
        self.assertTrue(pag.headers)
        self.assertTrue(pag.list_display)
        self.assertEqual(len(pag.headers),len(pag.list_display))
        self.assertTrue(pag.astable)
        for c,head in zip(self.heads,pag.list_display):
            self.assertEqual(c,head.code)
        return pag
        
    def testTablePagination(self):
        self.pagination()
        
    def testSimple(self):
        p = self.pagination()
        tbl = p.widget(())
        ht = tbl.render()
        self.assertTrue('<table>' in ht)
        self.assertTrue('</table>' in ht)
        self.assertTrue('<thead>' in ht)
        self.assertTrue('</thead>' in ht)
        self.assertTrue('<tbody>' in ht)
        self.assertTrue('</tbody>' in ht)
        self.assertFalse('<tfoot>' in ht)
        self.assertFalse('</tfoot>' in ht)
        self.assertTrue('<tbody>\n</tbody>' in ht)
        self.assertTrue('</tbody>\n</table>' in ht)
        
    def testSimpleFooter(self):
        p = self.pagination(footer = True)
        tbl = p.widget(())
        ht = tbl.render()
        self.assertTrue('<table>' in ht)
        self.assertTrue('</table>' in ht)
        self.assertTrue('<thead>' in ht)
        self.assertTrue('</thead>' in ht)
        self.assertTrue('<tbody>' in ht)
        self.assertTrue('</tbody>' in ht)
        self.assertTrue('<tfoot>' in ht)
        self.assertTrue('</tfoot>' in ht)
        self.assertTrue('<tbody>\n</tbody>' in ht)
        self.assertFalse('</tbody>\n</table>' in ht)
        self.assertTrue('</tbody>\n<tfoot>' in ht)
        self.assertTrue('</tfoot>\n</table>' in ht)
        
    def testTableWithData(self):
        p = self.pagination(ajax = False)
        self.assertFalse(p.ajax)
        data = zip(('pippo','pluto','luna'),(3,4,1))
        tbl = p.widget(data)
        ht = tbl.render()
        self.assertTrue('<td>pippo</td>\n<td>3</td>' in ht)
        self.assertTrue('<td>pluto</td>\n<td>4</td>' in ht)
        self.assertTrue('<td>luna</td>\n<td>1</td>' in ht)
        
    