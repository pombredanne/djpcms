import sys
import os

from djpcms.utils import test
from djpcms.core import fetch_command, execute, Command


class CommandTests(test.TestCase):
    
    def testServe(self):
        c = fetch_command(self.website(), 'serve')
        self.assertTrue(isinstance(c,Command))
        self.assertEqual(c.help,\
"Serve the application using WSGIserver from the standard library.")
        self.assertEqual(len(c.option_list),2)
        
    def testServeDry(self):
        argv = sys.argv[:1] + ['serve','9000','--dryrun']
        execute(self.website(), argv)
        
    def testEnvironment(self):
        argv = sys.argv[:1] + ['environ']
        execute(self.website(), argv)
        
    def testStyle(self):
        argv = sys.argv[:1] + ['style','-t','teststyle']
        cmd = execute(self.website(), argv)
        self.assertEqual(cmd.theme,'teststyle')
        os.remove(cmd.target)
        
    def testShell(self):
        c = fetch_command(self.website(), 'shell')
        self.assertTrue(isinstance(c,Command))