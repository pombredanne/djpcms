'''Test Application construction'''
from djpcms import views, cms
from djpcms.utils import test


class TestViews(test.TestCase):
    
    def testDefaultView(self):
        '''Construct a simple view'''
        v = views.View('foo/', renderer = lambda djp : 'foo')
        self.assertEqual(v.name,'foo')
        self.assertEqual(v.description,'Foo')
        self.assertEqual(v.path,'/foo/')
        self.assertEqual(v.route.path,'/foo/')
        self.assertEqual(v.form,None)
        self.assertEqual(v.in_nav,0)
        self.assertFalse(v.isbound)
        self.assertEqual(v.render(None),'foo')

    def testViewLevel2(self):
        v = views.View('foo/bla/', renderer = lambda djp : 'foo')
        self.assertEqual(v.name,'foo_bla')
        self.assertEqual(v.description,'Foo bla')
        self.assertEqual(v.path,'/foo/bla/')
        self.assertEqual(v.route.path,'/foo/bla/')
        self.assertEqual(v.route.level,2)
        self.assertEqual(v.form,None)
        self.assertEqual(v.in_nav,0)
        self.assertFalse(v.isbound)
        self.assertEqual(v.render(None),'foo')
        
    def testViewWithInputs1(self):
        v = views.View('foo/',
                       name = 'home',
                       description = 'Home Page',
                       renderer = lambda djp : 'foo home')
        self.assertEqual(v.name,'home')
        self.assertEqual(v.description,'Home Page')
        self.assertEqual(v.path,'/foo/')
        self.assertEqual(v.route.path,'/foo/')
        self.assertEqual(v.form,None)
        self.assertEqual(v.in_nav,0)
        self.assertFalse(v.isbound)
        self.assertEqual(v.render(None),'foo home')
        
    def testViewView(self):
        v = views.ViewView()
        self.assertFalse(v.isbound)
        self.assertEqual(v.parent_view,None)
        self.assertEqual(v.parent,None)
        self.assertEqual(v.route,v.rel_route)
        self.assertEqual(v.path,'/<id>/')
        
    def testChangeView(self):
        v = views.ChangeView()
        self.assertFalse(v.isbound)
        self.assertEqual(v.parent_view,'view')
        self.assertEqual(v.parent,None)
        self.assertEqual(v.route,v.rel_route)
        self.assertEqual(v.path,'/change')
        
    def testDeleteView(self):
        v = views.DeleteView()
        self.assertFalse(v.isbound)
        self.assertEqual(v.parent_view,'view')
        self.assertEqual(v.parent,None)
        self.assertEqual(v.route,v.rel_route)
        self.assertEqual(v.path,'/delete')
        v = views.DeleteView('del')
        self.assertEqual(v.path,'/del')
        self.assertEqual(v.parent_view,'view')
        self.assertEqual(v.parent,None)
        self.assertTrue(v.route.is_leaf)


class TestSimpleApplication(test.TestCase):
        
    def testContruction1(self):
        '''Construct an Application with 1 view'''
        app = views.Application('/',
                    name = 'luca',
                    routes = (views.View(renderer = lambda djp : 'ciao'),))
        self.assertFalse(app.isbound)
        self.assertEqual(app.parent,None)
        self.assertEqual(app.count(),1)
        self.assertEqual(len(app),1)
        
    def testContruction2(self):
        '''Construct an Application with 2 views'''
        view1 = views.View(renderer = lambda djp : 'ciao')
        view2 = views.View('foo/', renderer = lambda djp : 'foo')
        self.assertEqual(view1.appmodel,None)
        self.assertEqual(view2.appmodel,None)
        self.assertEqual(view1.path,'/')
        self.assertEqual(view2.path,'/foo/')
        app = views.Application('/', routes = (view2,view1))
        self.assertEqual(view1.appmodel,None)
        self.assertEqual(view2.appmodel,None)
        self.assertFalse(app.isbound)
        self.assertEqual(app.parent, None)
        self.assertEqual(app.root, app)
        self.assertEqual(app.count(),2)
        self.assertEqual(len(app),2)
        self.assertFalse(app.base_routes) # no base routes from metaclass
        # views get copied so instances are not the same
        self.assertNotEqual(app.root_view,view1)
        self.assertEqual(app.root_view.path,view1.path)
        
    def testUrlException(self):
        app = views.Application('/')
        app2 = self.assertRaises(cms.UrlException,
                                 views.Application, 'foo/', parent_view='/')
        
        
        