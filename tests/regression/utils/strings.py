import unittest
from djpcms.utils import force_str


__all__ = ['TestUtilsStrings']


class TestUtilsStrings(unittest.TestCase):

    def test_force_str(self):
        ts = bytes('test string','utf-8')
        self.assertEqual(force_str(ts),'test string')
    
