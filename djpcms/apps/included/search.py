'''\
Search Applications with Tags.
'''
from djpcms import views, forms, html, sites, ajax
from djpcms.plugins.apps import HtmlSearchForm


class SearchQuery(views.View):
    '''This view renders as a search box'''
    isplugin = True
    astable = True
    
    @property
    def engine(self):
        return self.appmodel.engine
        
    def render(self, djp):
        return self.get_form(djp).render(djp)


class SearchView(SearchQuery):
    '''This view renders the search results'''    
    
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
    
    def render(self, djp):
        qs = self.appquery(djp)
        return ''
    
    def ajax__autocomplete(self, djp):
        qs = self.appquery(djp)
        params = djp.request.REQUEST
        if 'maxRows' in params:
            qs = qs[:int(params['maxRows'])]
        return ajax.CustomHeaderBody('autocomplete',
                                     list(self.appmodel.gen_autocomplete(qs)))
        
    
class Application(views.Application):
    for_models = None
    engine = None
        
    #query = SearchQuery(form = HtmlSearchForm,
    #                    form_method = 'GET',
    #                    form_ajax = False,
    #                    description = 'Seach Form')
    #search = SearchView(regex = 'search-results',
    #                    form = HtmlSearchForm,
    #                    form_method = 'GET',
    #                    description = 'Search Results')
    search = SearchView(form = HtmlSearchForm,
                        form_method = 'GET',
                        description = 'Search Results')
    search_model = SearchView(regex = '(?P<model>{0})'.format(views.SLUG_REGEX),
                              form = HtmlSearchForm,
                              form_method = 'GET',
                              form_ajax = False,
                              description = 'Seach Model')
    
    def __init__(self,*args,**kwargs):
        self.engine = kwargs.pop('engine',None) or self.engine
        if not self.engine:
            raise ValueError('Search engine not available')
        self.engine.web_hook = self
        sites.search_application = self 
        super(Application,self).__init__(*args,**kwargs)


    

