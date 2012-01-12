import markdown

from djpcms.utils import markups
    

class Application(markups.Application):
    code = 'markdown'
    name = 'Markdown'
    
    def __call__(self, request, text):
        return markdown.markdown(text)
    
    