try:
    from style import *
except ImportError:
    import sys
    import os
    sys.path.append(os.path.join(os.path.split(os.path.abspath(__file__))[0],
                                 '_style'))
    from style import *

