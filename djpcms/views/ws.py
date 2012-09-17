from copy import deepcopy

from pulsar.apps import ws

from djpcms import cms

from .application import ApplicationBase

__all__ = ['WsView', 'WebSocketApp']


class WsView(cms.RouteMixin, ws.WS):
    
    def __init__(self, route=None):
        super(WsView, self).__init__(route or '/')
        
    def on_open(self, request):
        pass
    
    def on_message(self, request, msg):
        pass
    
    def on_close(self, request):
        pass


class WebSocketRequest:
    
    def __init__(self, environ, view, urlargs):
        self.environ = environ
        self.view = view
        self.urlargs = urlargs
    
    def on_open(self):
        return self.view.on_open(self)
    
    def on_message(self, msg):
        return self.view.on_message(self, msg)
    

class WebSocketApp(ApplicationBase, cms.ResolverMixin, ws.WS):
    ViewClass = WsView
    
    def match(self, environ):
        view_args = cms.ResolverMixin.match(self,
                                            environ.get('PATH_INFO', '/')[1:])
        if view_args:
            environ['websocket-request'] = WebSocketRequest(environ, *view_args)
            return True
    
    def on_open(self, environ):
        return environ['websocket-request'].on_open()
        
    def on_message(self, environ, msg):
        return environ['websocket-request'].on_message(msg)
    
    def on_close(self, environ):
        return environ['websocket-request'].on_close()
    
    def _load(self):
        routes = []
        for route in self.base_routes:
            route = deepcopy(route)
            routes.append(route)
        for route in sorted(routes, key=lambda x: x.route_ordering):
            if route.path == '/':
                self.root_view = route
            self.routes.append(route)
        return tuple(self)
    