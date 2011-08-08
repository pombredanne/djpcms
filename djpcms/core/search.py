

class Search(object):
    '''Utility class for searching models'''
        
    def __init__(self, engine = None, model = None):
        self._engine = engine
        self.model = model
        
    @property
    def engine(self):
        if not self._engine and self.model:
            self._engine = getattr(self.model._meta,'searchengine',None)
        return self._engine
            
    def url(self, djp):
        if self.model:
            app = djp.site.for_model(self.model, all = True)
            if app:
                return app.path
        else:
            return '/search/'