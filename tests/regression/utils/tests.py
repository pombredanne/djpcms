import sys

from .strings import *
from .regexurl import *
from .crypt import *

if sys.version_info < (2,7):
    from ordereddict import *