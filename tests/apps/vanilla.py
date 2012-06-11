'''Vanilla Application'''
import os

from djpcms import views, cms
from djpcms.utils import test
from djpcms.apps.vanilla import Application
    

class TestVanillaMeta(test.TestCase):
    installed_apps = ('stdcms','examples')
    
    def urls(self, site):
        from tests.models import Portfolio
        return (Application('/portfolio/', Portfolio),)
    
    def testApplication(self):
        app = Application('/')
        self.assertEqual(len(app),5)
        self.assertFalse(app.isbound)
        self.assertEqual(app[0].name,'search')
        self.assertEqual(app[1].name,'add')
        self.assertEqual(app[2].name,'view')
        self.assertEqual(app[3].name,'change')
        self.assertEqual(app[4].name,'delete')
        
    @test.skipUnless(os.environ.get('stdcms'), "Requires stdcms installed")
    def testParentViews(self):
        from tests.models import Portfolio
        site = self.website()()
        app = site[0]
        self.assertEqual(app.model, Portfolio)
        self.assertEqual(app.mapper.model, Portfolio)
        self.assertEqual(len(app),5)
        self.assertTrue(app.isbound)
        self.assertEqual(len(site.urls()),1)
        self.assertEqual(len(app.urls()),5)
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
        
    @test.skipUnless(os.environ.get('stdcms'), "Requires stdcms installed")
    def testRoutes(self):
        site = self.website()()
        app = site[0]
        self.assertEqual(len(app),5)
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
    
    @test.skipUnless(os.environ.get('stdcms'), "Requires stdcms installed")    
    def testGetViews(self):
        site = self.website()()
        app = site[0]
        self.assertEqual(app.views.get('search').name,'search')
        self.assertEqual(app.views.get('view').name,'view')
        self.assertEqual(app.views.get('add').name,'add')
        self.assertEqual(app.views.get('change').name,'change')
        self.assertEqual(app.views.get('delete').name,'delete')
        self.assertRaises(KeyError,lambda : app.views['bla'])
    
    @test.skipUnless(os.environ.get('stdcms'), "Requires stdcms installed")
    def testSubApplicationMeta(self):
        from tests.models import Portfolio, User
        self.assertRaises(cms.UrlException, lambda : Application('/',\
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
        
    @test.skipUnless(os.environ.get('stdcms'), "Requires stdcms installed")
    def testSubApplicationMeta2(self):
        from tests.models import Portfolio, User
        port = Application('portfolio/',
                           Portfolio,
                           parent_view = 'view',
                           related_field = 'user',
                           routes = (views.ViewView('<pid>/', name = 'view'),))
        app = Application('bla/', User, routes=(port,))
        site = cms.Site(cms.get_settings(APPLICATION_URLS=(app,)))
        view, urlargs = site.resolve('bla/56/portfolio/')
        urls = app.urls()
        self.assertEqual(len(urls),6)
        self.assertEqual(urlargs,{'id':'56'})
        self.assertEqual(view,port.views['search'])
        view, urlargs = site.resolve('bla/56/portfolio/myportfolio/')
        self.assertEqual(urlargs,{'id':'56','pid':'myportfolio'})
    
    def testRequestHome(self):
        client = self.client()
        response = client.get('/')
        self.assertEqual(response.status_code,200)
        