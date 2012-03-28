#!/usr/bin/env python
'''djpcms test suite. Requires pulsar or nose.'''
import sys
import os

from djpcms.utils import test, Path
# Check if stdcms is available. If so we enable several tests.
try:
    import stdcms
except:
    stdcms = None
        
def add_nose_options(argv):
    test.addoption(argv, '-w', value = 'tests/regression')
    test.addoption(argv, '--all-modules')
    
def start():
    os.environ['stdcms'] = 'stdcms' if stdcms else ''
    # Add the example directory to the python path
    path = Path(__file__)
    path.add2python(down = ('examples',))
    test.start(nose_options = add_nose_options)

if __name__ == '__main__':
    start()