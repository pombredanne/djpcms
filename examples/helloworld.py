'''\
djpcms Hello world Example.
To run the server simply::

    python helloworld.py serve
'''
from djpcms import cms, views

class HelloWorld(cms.WebSite):
    
    def load(self):
        settings = cms.get_settings(__file__,
                                    APPLICATION_URLS=self.urls,
                                    DEBUG=True)
        return cms.Site(settings)
    
    def urls(self, site):
        '''Create a tuple with one application containing one view'''
        return (
            views.Application('/',
                name = 'Hello world example',
                routes = (views.View(renderer=lambda request : 'Hello world!'),)
            ),)


if __name__ == '__main__':
    cms.execute(HelloWorld())

