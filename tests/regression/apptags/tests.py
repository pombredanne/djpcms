from djpcms import test
from djpcms.apps.included.tagging import cleaned_tags



class TestTagApp(test.TestCase):
    
    def testCleaned(self):
        self.assertEqual(tuple(cleaned_tags('baa foo   bee')),
                         ('baa','foo','bee'))
        self.assertEqual(tuple(cleaned_tags('baa, foo  ,   ,,    ,  bee', separator = ',')),
                         ('baa','foo','bee'))