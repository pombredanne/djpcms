import djpcms
from djpcms.views import Application,View

def urls():
    '''Create a tuple with one application containg one view'''
    return (
        Application('/',
            name = 'Hello world!',
            home = View(renderer = lambda djp : 'Hello world!')
        ),)
             
djpcms.MakeSite(__file__,
                APPLICATION_URLS = urls,
                DEFAULT_TEMPLATE_NAME = ('djpcms/simple.html',),
                DEBUG = True,
                )

if __name__ == '__main__':
    '''To run type python helloworld.py serve'''
    djpcms.execute(djpcms.sites)

    