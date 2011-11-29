import djpcms
from djpcms import views, http, Route, ImproperlyConfigured, AlreadyRegistered
from djpcms.utils import test, zip


def get_simpleapps():
    return (
        views.Application('/bla/',
            name = 'app2',
            routes = (views.View(renderer = lambda djp : 'ciao bla'),
                      views.View('pluto/',\
                                    renderer = lambda djp : 'ciao bla view2'))
        ),
        views.Application('/',
            name = 'app1',
            routes = (views.View(renderer = lambda djp : 'ciao'),)
        ),
    )

    
class TestApplication(test.TestCase):

    def setUp(self):
        settings = djpcms.get_settings(__file__,
                                       APPLICATION_URLS = get_simpleapps)
        self.site = site = djpcms.Site(settings = settings)
        self.assertEqual(site.parent,None)
        self.assertEqual(site.path,'/')
        
    def testBindning(self):
        site = self.site
        self.assertFalse(site.isbound)
        urls = site.urls()
        self.assertEqual(len(urls),2)
        self.assertTrue(site.isbound)
        # loop over application urls
        for app in urls:
            self.assertTrue(app.isbound)
            self.assertEqual(app.parent,site)
            self.assertEqual(app.root,site)
        app1 = site.routes[0]
        self.assertEqual(len(app1),2)
        app2 = site.routes[1]
        self.assertEqual(len(app2),1)
            
    def testSimpleResolve(self):
        site = self.site
        handle, urlargs = site.resolve('')
        self.assertEqual(urlargs,{})
        self.assertEqual(handle.path,'/')
        self.assertEqual(handle.root,site)
        self.assertEqual(handle.parent.parent,site)
        
    def testSimpleResolve2(self):
        site = self.site
        handle, urlargs = site.resolve('bla/')
        self.assertTrue(handle.isbound)
        self.assertEqual(urlargs,{})
        self.assertEqual(handle.path,'/bla/')
        self.assertEqual(handle.root,site)
        self.assertEqual(handle.parent.parent,site)

        
