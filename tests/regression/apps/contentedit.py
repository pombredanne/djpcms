from djpcms.utils import test


class ContentEditMeta(test.TestCase):
    
    def testApplication(self):
        from djpcms.apps.contentedit import ContentApplication
        app = ContentApplication('edit/')
        self.assertEqual(len(app),5)
        