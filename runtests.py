#!/usr/bin/env python
'''djpcms test suite. Requires pulsar::

    pip install pulsar
'''
import sys
import os

try:
    import pulsar
except ImportError:
    pulsar = None
    
try:
    import nose
except:
    nose = None

import djpcms

if pulsar:
    from pulsar.apps.test import TestSuite, TestOptionPlugin
    from pulsar.apps.test.plugins import bench, httpclient

def noseoption(argv,*vals,**kwargs):
    if vals:
        for val in vals:
            if val in argv:
                return
        argv.append(vals[0])
        value = kwargs.get('value')
        if value is not None:
            argv.append(value)
    
def start():
    global pulsar
    argv = sys.argv
    if len(argv) > 1 and argv[1] == 'nose':
        pulsar = None
        sys.argv.pop(1)
    
    if pulsar:
        os.environ['djpcms_test_suite'] = 'pulsar'
        suite = TestSuite(
                    description = 'Djpcms Asynchronous test suite',
                    modules = ('tests',),
                    plugins = (bench.BenchMark(),
                               httpclient.HttpClient()))
        suite.start()
    elif nose:
        os.environ['djpcms_test_suite'] = 'nose'
        argv = list(sys.argv)
        noseoption(argv, '-w', value = 'tests/regression')
        noseoption(argv, '--all-modules')
        from tests import regression
        nose.main(argv=argv)
    else:
        print('To run tests you need either pulsar or nose.')
        exit(0)

if __name__ == '__main__':
    start()