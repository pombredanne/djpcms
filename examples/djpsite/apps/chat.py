from djpcms import forms, views, html, media
from djpcms.forms import layout as uni

from stdnet.apps import pubsub


class ChatForm(forms.Form):
    text = forms.CharField(required=False, widget=html.TextArea())
    
    def on_submit(self, commit):
        if commit:
            text = self.cleaned_data.get('text')
            if text:
                self.request.appmodel.publish('chat', text)
            


ChatFormHtml = forms.HtmlForm(
    ChatForm,
    layout=uni.FormLayout(default_style=uni.nolabel),
    inputs=(('submit','submit'),)
)

class ChatApplication(views.Application):
    _media = media.Media(js=['djpsite/chat.js'])
    publisher = pubsub.Publisher()
    subscriber = pubsub.Subscriber()
    home = views.View()
    chat = views.View('chat', form=ChatFormHtml, has_plugins=True)
    
    def publish(self, text):
        self.publisher.publish(text)
        
    def render(self, request, **kwargs):
        return html.Widget('div', cn='chatroom').render(request)
    
    def media(self, request):
        return self._media