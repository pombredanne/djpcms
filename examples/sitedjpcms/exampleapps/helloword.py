# Need this during development in windows ######
import os
import sys
p = lambda x : os.path.split(x)[0]
sys.path.insert(0,p(p(p(p(__file__)))))
################################################
#
import djpcms
from djpcms.views import Application,View

def urls():
    '''Create a tuple with one application containg one view'''
    return (
        Application('/',
            home = View(renderer = lambda djp : 'Hello World')
        ),)
             
djpcms.MakeSite(__file__,
                APPLICATION_URLS = urls,
                DEFAULT_TEMPLATE_NAME = ('djpcms/simple.html',),
                DEBUG = True,
                )

if __name__ == '__main__':
    '''To run type python helloworld.py serve'''
    djpcms.execute()

    