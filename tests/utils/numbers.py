from djpcms.utils import test
from djpcms.utils.numbers import significant, significant_format,\
                                 significant_format_old


class TestUtilsStrings(test.TestCase):

    def testSignificant(self):
        self.assertEqual(significant(2), 2)
        self.assertEqual(significant(2.1), 2.1)
        self.assertEqual(significant(2.153), 2.153)
        self.assertEqual(significant(2.153, n=3), 2.15)
        self.assertEqual(significant(2153.2), 2153)
        self.assertEqual(significant(2153.2, n=3), 2150)
        self.assertEqual(significant(215310876), 215300000)
        self.assertRaises(ValueError, significant, 'sjkcdbhsjcd')
        self.assertRaises(TypeError, significant, None)

    def testSignificantFormat(self):
        self.assertEqual(significant_format(2.1), '2.1')
        self.assertEqual(significant_format(2153.2), '2,153')
        self.assertEqual(significant_format(2153.2, n=10), '2,153.2')
        # try with a string
        self.assertEqual(significant_format('-45233.1', n=10), '-45,233.1')
        self.assertEqual(significant_format(123.5), '123.5')
