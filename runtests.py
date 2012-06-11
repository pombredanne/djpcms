#!/usr/bin/env python
'''djpcms test suite. Requires pulsar or nose.'''
import sys
import os

# Check if stdcms is available. If so we enable several tests.
try:
    import stdcms
except:
    stdcms = None
    
from djpcms.utils import test, path

        
def add_nose_options(argv):
    test.addoption(argv, '-w', value='tests')
    test.addoption(argv, '--all-modules')
    
def start():
    os.environ['stdcms'] = 'stdcms' if stdcms else ''
    # Add the example directory to the python path
    p = path.Path(__file__)
    p.add2python(down=('examples',))
    test.start(nose_options=add_nose_options,
               modules=('tests',))

if __name__ == '__main__':
    start()