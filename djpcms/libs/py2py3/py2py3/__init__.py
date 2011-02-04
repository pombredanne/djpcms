import os

from .base import *

if os.name == 'nt':
    from .windows import Platform
elif os.name == 'posix':
    from .posix import Platform
elif os.name == 'darwin':
    from .macos import Platform
else:
    raise RuntimeError("Platform {0} is not supported.".format(os.name))

platform = Platform()