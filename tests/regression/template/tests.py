from djpcms import test, sites



@test.skipUnless(sites.tests.TEMPLATE_ENGINE,"jinja2")
class TestJinja2Templates(test.TestCase):
    
    def loader(self):
        from djpcms.template import handle
        return handle('jinja2')
        
    def testLoader(self):
        loader = self.loader()
        self.assertEqual(len(loader.envs),1)
        
    def testSimpleRender(self):
        loader = self.loader()
        html = loader.render('simple.html',{'bar':5})
        html = html.strip()
        self.assertEqual(html,'35')