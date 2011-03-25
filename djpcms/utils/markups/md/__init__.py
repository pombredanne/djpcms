import markdown2

from djpcms.utils.markups import application
    
class Application(application.Application):
    code = 'md'
    name = 'Markdown'
    
    def __call__(self, text):
        return markdown2.markdown(text)
    
    
app = Application()