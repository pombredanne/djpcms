from .test import *
from .runner import build_suite, TestLoader, TestSuiteRunner
from .mixin import *


TEST_TYPES = {'regression': TestSuiteRunner,
              'bench': None,
              'profile': None}

