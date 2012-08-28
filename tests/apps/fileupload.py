from djpcms.utils import test


class TestUploadForm(test.TestCase):
        
    def testLayout(self):
        from djpcms.apps.fileupload import FileUploadForm
        f = FileUploadForm(action = '/bla/')
        layout = f.layout
        c = layout.allchildren[0]
        self.assertEqual(c.tag,None)
        html = f.render()
        self.assertTrue('button' in html)
        
    def testForm(self):
        from djpcms.apps.fileupload import FileUploadForm
        f = FileUploadForm(action = '/bla/')
        self.assertTrue(f.form)
        html = f.render()
        self.assertTrue("action='/bla/'" in html)