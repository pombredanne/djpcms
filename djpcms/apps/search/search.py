'''Search Applications which works with the SearchBox plugin.
'''
from djpcms import views, forms, html, ajax, ImproperlyConfigured, SLUG_REGEX

from .forms import HtmlSearchForm


def get_search_url(djp, for_model = None):
    if for_model:
        appmodel = djp.site.for_model(for_model, all = True)
        if appmodel and hasattr(appmodel.model._meta,'searchengine'):
            return appmodel.path
    else:
        engine = djp.site.search_engine
        if engine:
            return engine.path
    

class Search(object):
    '''Utility class for searching models'''
        
    def __init__(self, model = None):
        self.model = model
    
    #@property
    #def engine(self):
    #    if not self._engine and self.model:
    #        self._engine = getattr(self.model._meta,'searchengine',None)
    #    return self._engine
            
    def url(self, djp):
        '''Return the url for searching'''
        if self.model:
            app = djp.site.for_model(self.model, all = True)
            if app:
                return app.path
        search_app = djp.site.search_engine
        if search_app:
            return search_app.search_url(self.model)


class SearchView(views.View):
    '''This view renders the search results'''    
    isplugin = True
    
    @property
    def engine(self):
        return self.appmodel.engine
        
    def model(self, djp):
        if 'model' in djp.kwargs:
            name = djp.kwargs['model']
            for model in djp.site._registry:
                if str(model._meta) == name:
                    return model  
            
    def appquery(self, djp, force_prefix = True):
        '''This function implements the search query.
The query is build using the search fields specifies in
:attr:`djpcms.views.appsite.ModelApplication.search_fields`.
It returns a queryset.
        '''
        model = self.model(djp)
        f = self.get_form(djp, force_prefix = False)
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
    
    search = SearchView(form = HtmlSearchForm,
                        form_method = 'GET',
                        description = 'Search Results')
    search_model = SearchView(regex = '(?P<model>{0})'.format(SLUG_REGEX),
                              form = HtmlSearchForm,
                              form_method = 'GET',
                              form_ajax = False,
                              description = 'Seach Model')
    
    def __init__(self,*args,**kwargs):
        self.engine = kwargs.pop('engine',None) or self.engine
        self.forallsites = kwargs.pop('forallsites',True)
        if not self.engine:
            raise ImproperlyConfigured('Search engine not available')
        super(Application,self).__init__(*args,**kwargs)

    def registration_done(self):
        '''Set the search engine application in the site.'''
        self.site._search_engine = self
        root = self.site.root
        if not root._search_engine and self.forallsites:
            root._search_engine = self

    def search_url(self, model):
        if model:
            return '{0}{1}/'.format(self.path,model)
        else:
            return self.path
    

