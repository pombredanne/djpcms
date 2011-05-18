'''\
djpcms Hello world Example.
To run the server simply::

    python helloworld.py serve
'''
import djpcms
from djpcms.views import Application,View


class Loader(object):
    loaded = False
    def __call__(self):
        if not self.loaded:
            self.loaded = True
            djpcms.MakeSite(__file__,
                            APPLICATION_URLS = self.urls,
                            DEFAULT_TEMPLATE_NAME = ('djpcms/simple.html',),
                            DEBUG = True,
                            )
        return djpcms.sites
    
    def urls(self):
        '''Create a tuple with one application containg one view'''
        return (
            Application('/',
                name = 'Hello world!',
                home = View(renderer = lambda djp : 'Hello world!')
            ),)


if __name__ == '__main__':
    '''To run type python helloworld.py serve'''
    djpcms.execute(Loader())

    