from djpcms import views
from stdcms.websocket import WsView


class WebSocketApps(views.WebSocketApp):
    chat = WsView('chat')
    
    