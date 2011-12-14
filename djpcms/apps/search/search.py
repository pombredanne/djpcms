from djpcms import views, forms, html, ajax, ImproperlyConfigured


def get_search_url(request, for_model = None):
    if for_model:
        appmodel = request.for_model(for_model)
        if appmodel and hasattr(appmodel.model._meta,'searchengine'):
            return appmodel.path
    else:
        engine = djp.site.search_engine
        if engine:
            return engine.path
    

class Search(object):
    '''Utility class for providing searching urls for models lazily.
You can use this in an autocomplete form fields.
    
:parameter model: Optional model to search

If no model is provided, a global search view must be available.
'''
        
    def __init__(self, model = None):
        self.model = model
    
    def url(self, request):
        '''Return the url for searching'''
        if self.model:
            app = request.for_model(model = self.model)
            if app:
                return app.url
        search_app = request.view.search_engine
        if search_app:
            return search_app.search_url(self.model)


class SearchView(views.View):
    '''This view renders the search results'''    
    has_plugins = True
    
    @property
    def engine(self):
        return self.appmodel.engine
        
    def get_model(self, request):
        if 'model' in request.urlargs:
            name = djp.urlargs['model']
            return request.for_model(name)  
            
    def query(self, request, force_prefix = True):
        '''This function implements the search query.
        '''
        model = self.get_model(request)
        f = self.get_form(request, force_prefix = False)
        if f.is_valid():
            q = f.form.cleaned_data['q']
            if q:
                return self.engine.search(q,include=model)
    
    def ajax__autocomplete(self, djp):
        qs = self.appquery(djp)
        params = djp.request.REQUEST
        if 'maxRows' in params:
            qs = qs[:int(params['maxRows'])]
        return ajax.CustomHeaderBody('autocomplete',
                                     list(self.appmodel.gen_autocomplete(qs)))
        
    
class Application(views.Application):
    engine = None
    in_nav = 0
    
    search = SearchView(description = 'Search Results')
    search_model = SearchView('<model>/',
                              description = 'Search Model')
    
    def __init__(self,*args,**kwargs):
        self.engine = kwargs.pop('engine',None) or self.engine
        self.forallsites = kwargs.pop('forallsites',True)
        if not self.engine:
            raise ImproperlyConfigured('Search engine not available')
        super(Application,self).__init__(*args,**kwargs)

    def on_bound(self):
        '''Set the search engine application in the site.'''
        if self.forallsites:
            site = self.root
        else:
            site = self.site
        site.internals['search_engine'] = self

    def search_url(self, model):
        if model:
            return '{0}{1}/'.format(self.path,model)
        else:
            return self.path
    

