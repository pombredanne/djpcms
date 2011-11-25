#!/usr/bin/env python
'''djpcms test suite. Requires pulsar::

    pip install pulsar
'''
from pulsar.apps.test import TestSuite, TestOptionPlugin
from pulsar.apps.test.plugins import bench, httpclient


class ORM(TestOptionPlugin):
    flags = ["--cms"]
    desc = 'Backend for CMS models'
    default = ''
    
    def configure(self, cfg):
        settings.DEFAULT_BACKEND = cfg.server
        
    
def suite():
    return TestSuite(description = 'Djpcms Asynchronous test suite',
                     modules = ('tests',),
                     plugins = (bench.BenchMark(),
                                httpclient.HttpClient())
                     )


if __name__ == '__main__':    
    suite.start()

    