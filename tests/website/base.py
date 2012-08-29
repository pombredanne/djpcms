__test__ = False
from djpcms.utils import test
skipUnless = test.skipUnless

try:
    from stdcms.utils import test
    import social
    installed = True
except ImportError:
    installed = False


@skipUnless(installed, 'Requires stdcms and social packages')
class TestCase(test.TestCase):

    def website(self):
        from djpsite.manage import WebSite
        if not hasattr(self, '_website'):
            self._website = WebSite(DEBUG=False,
                                    SESSION_COOKIE_NAME='djpsite-test',
                                    SECRET_KEY='djpsite-test')
        return self._website

    def site(self):
        return self.website()()

    def _pre_setup(self):
        self.flush()
        self._create_users()

    def _post_teardown(self):
        self.flush()

    def flush(self):
        site = self.site()

    def _create_users(self):
        pass