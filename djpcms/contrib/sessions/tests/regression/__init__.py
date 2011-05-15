from djpcms import test

from djpcms.contrib.sessions.models import Session


class TestSessions(test.TestCase):
             
    def testCreate(self):
        s = Session.objects.create()
        self.assertTrue(s.id)