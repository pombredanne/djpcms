from djpcms.utils import test


class DocsMeta(test.TestCase):
    
    def testApplication(self):
        from djpcms.apps import docs
        app = docs.DocApplication('docs/')
        self.assertEqual(len(app),2)