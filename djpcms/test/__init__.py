from .test import TestCase, TestCaseWithUser, PluginTest,\
                  skip, skipIf, skipUnless, SkipTest,\
                  TestDirectory, ContribTestDirectory,\
                  SiteTestDirectory
from .runner import build_suite, TestLoader, TestSuiteRunner


TEST_TYPES = {'regression': TestSuiteRunner,
              'bench': None,
              'profile': None}

