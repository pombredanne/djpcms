#!/usr/bin/env python
'''djpcms test suite. Requires pulsar::

    pip install pulsar
'''
import pulsar
from pulsar.apps.test import TestSuite, TestOptionPlugin
from pulsar.apps.test.plugins import bench, httpclient


class ORM(TestOptionPlugin):
    flags = ["--cms"]
    desc = 'Backend for CMS models'
    default = ''
    
    def configure(self, cfg):
        settings.DEFAULT_BACKEND = cfg.server
        
    

if __name__ == '__main__':    
    suite = TestSuite(description = 'Djpcms Asynchronous test suite',
                      modules = ('tests',),
                      plugins = (bench.BenchMark(),
                                 httpclient.HttpClient())
                      )
    
    suite.start()

    