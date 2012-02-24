import markdown

from . import base
    

class Application(base.Application):
    code = 'markdown'
    name = 'Markdown'
    
    def __call__(self, request, text):
        return markdown.markdown(text)
    
    