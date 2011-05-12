from djpcms import test, sites
from djpcms.apps.included.vanilla import Application


def appurls():
    from regression.related.models import Holder, Item
    return Application('/',
                       Holder,
                       name = 'test-app',
                       apps = (
                              Application('items',
                                          Item,
                                          parent = 'view'),
                              )
                       ),


@test.skipUnless(sites.tests.CMS_ORM,"Testing without ORM")
class TestRealtedApplication(test.TestCase):
    appurls = 'regression.related.tests.appurls'
    
    def testNames(self):
        site = self.site
        self.assertEqual(len(site),1)
        view = site.getapp('test_app')
        appmodel = view.appmodel
        self.assertEqual(view,appmodel.root_view)
        add = appmodel.getview('items-add')
        self.assertEqual(add.path(),'/%(id)s/items/add/')
        