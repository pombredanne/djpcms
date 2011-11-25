from djpcms.utils import test
from djpcms.apps import archive


@test.skipUnless(test.djpapps,"Requires djpapps installed")
class ArchiveApp(test.TestCase):
    
    def testSimple(self):
        pass
