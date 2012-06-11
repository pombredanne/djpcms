import os

from djpcms.utils import test


class AdminApp(test.TestCase):
    
    def testSimple(self):
        from djpcms.apps import admin
