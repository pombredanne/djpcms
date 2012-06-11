import unittest as test
import time
from datetime import date, datetime

from djpcms.utils.dates import smart_time


class Dates(test.TestCase):
    
    def testSmartTime(self):
        t = time.time()
        dte = datetime.fromtimestamp(t)
        self.assertEqual(len(smart_time(t)),5)
