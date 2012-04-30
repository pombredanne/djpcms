__test__ = False
from djpcms.utils import test
skipUnless = test.skipUnless

try:
    from stdcms.utils import test
    installed = True
except ImportError:
    installed = True


@skipUnless(installed, 'Requires stdcms')
class TestCase(test.TestCase):
    
    def website(self):
        from djpsite.manage import WebSite
        from stdnet import orm
        self.orm = orm
        if not hasattr(self, 'site'):
            self._website = WebSite(settings_file='djpsite.conf')
            self.site = self._website()
        return self._website
    
    def setUp(self):
        self.site = self.website()()
        self.assertTrue(self.orm.flush_models())
        
    def tearDown(self):
        self.orm.flush_models()
    
    