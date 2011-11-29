'''\
djpcms Hello world Example.
To run the server simply::

    python helloworld.py serve
'''
import djpcms
from djpcms.views import Application,View


class Loader(djpcms.SiteLoader):
    
    def load(self):
        settings = djpcms.get_settings(__file__,
                        APPLICATION_URLS = self.urls,
                        DEFAULT_TEMPLATE_NAME = ('djpcms/simple.html',),
                        DEFAULT_STYLE_SHEET = {},
                        DEFAULT_JAVASCRIPT = [])
        return djpcms.Site(settings)
    
    def urls(self):
        '''Create a tuple with one application containing one view'''
        return (
            Application('/',
                name = 'Hello world example',
                routes = (View(renderer = lambda request : 'Hello world!'),)
            ),)


if __name__ == '__main__':
    djpcms.execute(Loader())

    