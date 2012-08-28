from djpcms.utils import test


class TestFontAwesome(test.TestCase):
    installed_apps = ('djpcms.apps.fontawesome',)
    
    def testMeta(self):
        site = self.site()
        self.assertTrue('djpcms.apps.fontawesome' in\
                         site.settings.INSTALLED_APPS)
    