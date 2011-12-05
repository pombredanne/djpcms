'''Vanilla Application'''
import djpcms
from djpcms import views, Site, get_settings
from djpcms.utils import test
from djpcms.apps.vanilla import Application


def site_for_app(app):
    return Site(get_settings(INSTALLED_APPS = ('stdcms','examples'),
                             APPLICATION_URLS = (app,)))
    

class TestVanillaMeta(test.TestCase):
    
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
        from examples.models import Portfolio
        app = Application('/',Portfolio)
        site = site_for_app(app)
        self.assertEqual(app.model,Portfolio)
        self.assertEqual(app.mapper,None)
        self.assertEqual(len(app),5)
        self.assertFalse(app.isbound)
        self.assertEqual(len(site.urls()),1)
        self.assertTrue(app.isbound)
        self.assertEqual(app.mapper.model,Portfolio)
        self.assertEqual(len(app.urls()),5)
        self.assertTrue(app.isbound)
        search = app[0]
        add = app[1]
        view = app[2]
        change = app[3]
        delete = app[4]
        self.assertEqual(search.parent,app)
        self.assertEqual(add.parent,app)
        self.assertEqual(view.parent,app)
        self.assertEqual(change.parent,app)
        self.assertEqual(delete.parent,app)
        
    @test.skipUnless(test.djpapps,"Requires djpapps installed")
    def testRoutes(self):
        from examples.models import Portfolio
        app = Application('/portfolio/',Portfolio)
        site = Site(get_settings(APPLICATION_URLS = (app,)))
        self.assertEqual(len(app),5)
        self.assertFalse(app.isbound)
        self.assertEqual(len(site.urls()),1)
        self.assertEqual(len(app.urls()),5)
        self.assertTrue(app.isbound)
        search = app.views['search']
        add = app.views['add']
        view = app.views['view']
        change = app.views['change']
        delete = app.views['delete']
        self.assertEqual(search.path,'/portfolio/')
        self.assertEqual(add.path,'/portfolio/add')
        self.assertEqual(view.path,'/portfolio/<id>/')
        self.assertEqual(change.path,'/portfolio/<id>/change')
        self.assertEqual(delete.path,'/portfolio/<id>/delete')
    
    @test.skipUnless(test.djpapps,"Requires djpapps installed")    
    def testGetViews(self):
        from examples.models import Portfolio
        app = Application('/',Portfolio)
        self.assertEqual(app.views.get('search').name,'search')
        self.assertEqual(app.views.get('view').name,'view')
        self.assertEqual(app.views.get('add').name,'add')
        self.assertEqual(app.views.get('change').name,'change')
        self.assertEqual(app.views.get('delete').name,'delete')
        self.assertRaises(KeyError,lambda : app.views['bla'])
    
    @test.skipUnless(test.djpapps,"Requires djpapps installed")
    def testSubApplicationMeta(self):
        from examples.models import Portfolio, User
        self.assertRaises(djpcms.UrlException, lambda : Application('/',\
                           Portfolio, parent_view = 'view'))
        port = Application('portfolio/',
                           Portfolio,
                           name = 'portfolio',
                           parent_view = 'view',
                           related_field = 'user')
        self.assertEqual(port.parent_view,'view')
        self.assertEqual(port.related_field,'user')
        app = Application('bla/', User, routes = (port,))
        self.assertEqual(app.parent_view, None)
        self.assertEqual(len(app),6)
        # The last is the subapplication
        self.assertEqual(app[5],port)
        self.assertEqual(app.views['portfolio'],port)
        self.assertEqual(port.path,'/<id>/portfolio/')
        
    @test.skipUnless(test.djpapps,"Requires djpapps installed")
    def testSubApplicationMeta2(self):
        from examples.models import Portfolio, User
        port = Application('portfolio/',
                           Portfolio,
                           parent_view = 'view',
                           related_field = 'user',
                           routes = (views.ViewView('<pid>/', name = 'view'),))
        app = Application('bla/',
                          User,
                          routes = (port,))
        site = djpcms.Site(djpcms.get_settings(APPLICATION_URLS = (app,)))
        view, urlargs = site.resolve('bla/56/portfolio/')
        urls = app.urls()
        self.assertEqual(len(urls),6)
        self.assertEqual(urlargs,{'id':'56'})
        self.assertEqual(view,port.views['search'])
        view, urlargs = site.resolve('bla/56/portfolio/myportfolio/')
        self.assertEqual(urlargs,{'id':'56','pid':'myportfolio'})


@test.skipUnless(test.djpapps,"Requires djpapps installed")
class VanillaSite(test.TestCase):
    
    def build_site(self):
        from examples.models import Book
        app = Application('/',Book)
        settings = djpcms.get_settings(APPLICATION_URLS = (app,))
        return djpcms.Site(settings)
    
    def testRequestHome(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code,200)
        