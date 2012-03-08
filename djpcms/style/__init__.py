try:
    from pycss import *
except ImportError:
    import sys
    import os
    sys.path.append(os.path.join(os.path.split(os.path.abspath(__file__))[0],
                                 '_pycss'))
    from pycss import *

