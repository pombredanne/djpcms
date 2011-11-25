from djpcms.utils import test
from djpcms.apps import tagging


@test.skipUnless(test.djpapps,"Requires djpapps installed")
class AdminApp(test.TestCase):
    
    def testSimple(self):
        pass
