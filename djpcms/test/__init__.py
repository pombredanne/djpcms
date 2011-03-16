from .test import TestCase, TestCaseWithUser, PluginTest,\
                  skip, skipIf, skipUnless, SkipTest,\
                  TestDirectory, ContribTestDirectory,\
                  SiteTestDirectory
from .runner import build_suite, TestLoader, TestSuiteRunner
from .mixin import *


TEST_TYPES = {'regression': TestSuiteRunner,
              'bench': None,
              'profile': None}

