from djpcms import test
from djpcms.apps.included.vanilla import Application 

from .models import Strategy

def appurls():
    return (
            Application('/strategies/',Strategy),
            )


class TestAppViews(test.TestCase):
    appurls = 'regression.appvanilla.tests.appurls'
    
    def setUp(self):
        self.makesite()
        self.sites.load()
        
    def testParents(self):
        appmodel = self.sites.for_model(Strategy)
        search = appmodel.getview('search')
        view = appmodel.getview('view')
        self.assertEqual(view.parent,search)
        add_view = appmodel.getview('add')
        self.assertEqual(add_view.parent,search)
        edit = appmodel.getview('edit')
        self.assertEqual(edit.parent,view)
        
    def testParentsWithPages(self):
        Strategy(name='zorro').save()
        p  = self.makepage('search',Strategy)
        p1 = self.makepage('view',Strategy)
        p2 = self.makepage('edit',Strategy)
        self.assertEqual(p1.parent,p)
        self.assertEqual(p2.parent,p1)
        appmodel = self.site.for_model(Strategy)
        search = appmodel.getview('search')
        view = appmodel.getview('view')
        self.assertEqual(view.parent,search)
        edit = appmodel.getview('edit')
        self.assertEqual(edit.parent,view)
        self.login()
        v1 = self.get('/strategies/1/')['djp'].view
        v2 = self.get('/strategies/1/edit/')['djp'].view
        self.assertTrue(v2.parent,v1)
        
    def testParentsWithMultiplePages(self):
        Strategy(name='zorro').save()
        s  = self.makepage('search',Strategy)
        p = self.makepage('view',Strategy)
        p1 = self.makepage('view',Strategy,'1')
        self.assertEqual(p.application,p1.application)
        a  = self.makepage('edit',Strategy)
        a1 = self.makepage('edit',Strategy,parent=p1)
        self.assertEqual(a1.parent,p1)