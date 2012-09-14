from pulsar.apps import ws

from .urlresolvers import ResolverMixin


class websocket:
    
    def __call__(self, request, msg):
        pass
        

class WebSocketHandle(ws.WS):
    
    def on_open(self, environ):
        path = environ.get('PATH_INFO', '/')
        
    def on_message(self, environ, msg):
        return environ['websocket-hadler'](environ, msg)
    
    