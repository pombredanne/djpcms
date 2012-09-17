import json

from djpcms import forms, views, html, media
from djpcms.utils.text import to_string
from djpcms.forms import layout as uni

from stdnet.apps import pubsub
from stdcms.websocket import pubsub_server


class ChatForm(forms.Form):
    text = forms.CharField(required=False, widget=html.TextArea())
    
    def on_submit(self, commit):
        if commit:
            text = self.cleaned_data.get('text')
            if text:
                user = self.request.user
                msg = json.dumps({'user': to_string(user),
                                  'message': text})
                self.request.appmodel.publish('chat', msg)
        return True
        

ChatFormHtml = forms.HtmlForm(
    ChatForm,
    layout=uni.FormLayout(default_style=uni.nolabel),
    inputs=(('submit','submit'),)
)

class ChatApplication(views.Application):
    _media = media.Media(js=['djpsite/chat.js'])
    home = views.View()
    chat = views.View('chat', form=ChatFormHtml, has_plugins=True)
    
    def publish(self, channels, text):
        p = pubsub_server(self.settings)
        return p.publish(channels, text)
        
    def render(self, request, **kwargs):
        return html.Widget('div', cn='chatroom').render(request)
    
    def media(self, request):
        return self._media