#!/usr/bin/env python
'''djpcms test suite. Requires pulsar::

    pip install pulsar
'''
import sys
import os

from djpcms.utils.pathtool import AddToPath

# This is for development.
pt = AddToPath(__file__)
pulsar = pt.add(module='pulsar', up = 1, down = ('pulsar',))
pt.add(module='stdnet', up = 1, down = ('python-stdnet',))
pt.add(module='djpapps', up = 1, down = ('djpapps',))
###############################################################

if pulsar:
    from pulsar.apps.test import TestSuite, TestOptionPlugin
    from pulsar.apps.test.plugins import bench, httpclient

    
def suite():
    return TestSuite(description = 'Djpcms Asynchronous test suite',
                     modules = ('tests',),
                     plugins = (bench.BenchMark(),
                                httpclient.HttpClient())
                     )


if __name__ == '__main__':
    argv = sys.argv
    if len(argv) > 1 and argv[1] == 'nose':
        pulsar = None
        sys.argv.pop(1)
    
    if pulsar:
        os.environ['djpcms_test_suite'] = 'pulsar'
        suite = TestSuite(description = 'Djpcms Asynchronous test suite',
                     modules = ('tests',),
                     plugins = (bench.BenchMark(),
                                httpclient.HttpClient())
                     )
        suite.start()
    else:
        os.environ['djpcms_test_suite'] = 'nose'
        import nose
        nose.main()
