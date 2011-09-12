import logging

from djpcms import test, views, http

from sessions.models import Session,Log, get_session_cookie_name
from sessions.handlers import DatabaseHandler


def urls(self):
    return (
        views.Application('/',
            name = 'Hello world!',
            home = views.View(renderer = lambda djp : 'Hello world!')
        ),)


class TestSessions(test.TestCase):
    appurls = urls
    
    def setUp(self):
        self.makesite()
        
    def testCreate(self):
        s = Session.objects.create()
        self.assertTrue(s.id)
        self.assertTrue(s.expiry)
        self.assertFalse(s.expired)
        self.assertRaises(KeyError, lambda : s.user_id)
        
    def testCookie(self):
        res = self.get('/')
        self.assertTrue('Set-Cookie' in res)
        c = res['Set-Cookie']
        self.assertTrue(c)
        c = http.parse_cookie(c[1])
        sc = get_session_cookie_name()
        self.assertTrue(sc in c)
        id = c[sc]
        s = Session.objects.get(id = id)
        self.assertEqual(s.id,id)
        self.assertTrue(s.expiry)
        

class TestLogger(test.TestCase):
    
    def setUp(self):
        self.makesite()
        self.logger = logging.getLogger('test-databse-logger')
        self.logger.setLevel(logging.DEBUG)
        self.handler = DatabaseHandler(level = logging.DEBUG)
        self.logger.addHandler(self.handler)
        
    def tearDown(self):
        self.logger.removeHandler(self.handler)
        
    def testAdd(self):
        self.logger.info('this is a test')
        logs = Log.objects.all()
        self.assertTrue(logs)
        
    