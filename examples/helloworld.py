'''\
djpcms Hello world Example.
To run the server simply::

    python helloworld.py serve
'''
try:
    import djpcms
except ImportError:
    import sys
    sys.path.insert(0,'../')
    import djpcms
    
from djpcms.core import execute, WebSite, Site, get_settings
from djpcms.views import Application, View


class HelloWorld(WebSite):
    
    def load(self):
        settings = get_settings(__file__,
                                       APPLICATION_URLS=self.urls,
                                       DEBUG=True)
        return Site(settings)
    
    def urls(self, site):
        '''Create a tuple with one application containing one view'''
        return (
            Application('/',
                name = 'Hello world example',
                routes = (View(renderer=lambda request : 'Hello world!'),)
            ),)


if __name__ == '__main__':
    execute(HelloWorld())

    