import djpcms
from djpcms.utils import test
from djpcms.apps.vanilla import Application


class TestVanilla(test.TestCase):
    
    def testApplication(self):
        app = Application('/')
        self.assertEqual(len(app),5)
        self.assertFalse(app.isbound)
        self.assertEqual(app[0].name,'search')
        self.assertEqual(app[1].name,'add')
        self.assertEqual(app[2].name,'view')
        self.assertEqual(app[3].name,'change')
        self.assertEqual(app[4].name,'delete')
        
    @test.skipUnless(test.djpapps,"Requires djpapps installed")
    def testParentViews(self):
        from examples.testmodels import Portfolio
        app = Application('/',Portfolio)
        self.assertEqual(len(app),5)
        self.assertFalse(app.isbound)
        self.assertEqual(len(app.urls()),5)
        self.assertTrue(app.isbound)
        search = app[0]
        add = app[1]
        view = app[2]
        change = app[3]
        delete = app[4]
        self.assertEqual(search.parent,app)
        self.assertEqual(add.parent,search)
        self.assertEqual(view.parent,search)
        self.assertEqual(change.parent,view)
        self.assertEqual(delete.parent,view)