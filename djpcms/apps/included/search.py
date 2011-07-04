'''Search Applications which works with the SearchBox plugin.
'''
from djpcms import views, forms, html, ajax
from djpcms.plugins.apps import HtmlSearchForm



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
    search_model = SearchView(regex = '(?P<model>{0})'.format(views.SLUG_REGEX),
                              form = HtmlSearchForm,
                              form_method = 'GET',
                              form_ajax = False,
                              description = 'Seach Model')
    
    def __init__(self,*args,**kwargs):
        self.engine = kwargs.pop('engine',None) or self.engine
        self.forallsites = kwargs.pop('forallsites',True)
        if not self.engine:
            raise ValueError('Search engine not available')
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
    

