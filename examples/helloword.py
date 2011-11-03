'''\
djpcms Hello world Example.
To run the server simply::

    python helloworld.py serve
'''
import djpcms
from djpcms.views import Application,View


class Loader(djpcms.SiteLoader):
    
    def default_load(self):
        self.sites.make(__file__,
                        APPLICATION_URLS = self.urls,
                        DEFAULT_TEMPLATE_NAME = ('djpcms/simple.html',)
                        )
    
    def urls(self):
        '''Create a tuple with one application containg one view'''
        return (
            Application('/',
                name = 'Hello world!',
                home = View(renderer = lambda djp : 'Hello world!')
            ),)


if __name__ == '__main__':
    djpcms.execute(Loader())

    