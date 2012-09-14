'''Test Websocket Application construction'''
from djpcms import views, cms
from djpcms.utils import test


class TestWS(test.TestCase):
    
    def testWebsocketApp(self):
        class WA(views.WebSocketApp):
            home = views.WsView()
        #
        self.assertEqual(len(WA.base_routes), 1)
        wa = WA('/ws/')
        self.assertEqual(wa.path, '/ws/')
        #
        view, urlargs = wa.resolve('')
        self.assertTrue(isinstance(view, views.WsView))
        self.assertFalse(urlargs)
        