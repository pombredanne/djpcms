from djpcms.utils import test


class ArchiveMeta(test.TestCase):
    
    def testApplication(self):
        from djpcms.apps import archive
        
        
@test.skipUnless(test.djpapps,"Requires djpapps installed")
class ArchiveApp(test.TestCase):
    
    def testApplication(self):
        from djpcms.apps import archive
