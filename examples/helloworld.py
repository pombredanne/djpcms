'''\
djpcms Hello world Example.
To run the server simply::

    python helloworld.py serve
'''
from djpcms import cms, views

class HelloWorld(cms.WebSite):
    
    def load(self):
        settings = cms.get_settings(__file__, APPLICATION_URLS=self.urls)
        return cms.Site(settings)
    
    def urls(self, site):
        '''Create a tuple with one application containing one view'''
        return (
            views.Application('/',
                routes = (views.View(renderer=lambda request : 'Hello World!'),)
            ),)


if __name__ == '__main__':
    cms.execute(HelloWorld())

