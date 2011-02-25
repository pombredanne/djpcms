'''I use this script to run tests on a windows development environment where
several libraries are under development.
No need to use this in Linux
'''
import os
from djpcms.utils.pathtool import AddToPath, uplevel
from runtests import run

pt = AddToPath(uplevel(os.path.abspath(__file__)))

pt.add(module='stdnet', uplev = 1, down = ('python-stdnet',))

if __name__ == '__main__':
    run()
    


 