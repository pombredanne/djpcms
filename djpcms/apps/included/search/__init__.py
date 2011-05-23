'''\
Search Applications with Tags.
'''
from djpcms import views, forms, html
from djpcms.forms.layout import DivFormElement, FormLayout, nolabel

#
#___________________________________________ A CLASSY SEARCH FORM
class SearchForm(forms.Form):
    '''
    A simple search form used by plugins.apps.SearchBox.
    The search_text name will be used by SearchViews to handle text search
    '''
    q = forms.CharField(required = False,
                        widget = html.TextInput(cn = 'classy-search autocomplete-off',
                                                title = 'Enter your search text'))

SearchSubmit = html.HtmlWrap(tag = 'div', cn='cx-submit',
                             inner = html.SubmitInput(cn='cx-search-btn '+forms.NOBUTTON,
                                                      title = 'Search').render())
HtmlSearchForm = forms.HtmlForm(
        SearchForm,
        inputs = [SearchSubmit],
        layout = FormLayout(
                    DivFormElement('q',
                                   default_style = nolabel,
                                   cn = 'cx-input'),
                    template = ('search_form.html',
                                'djpcms/components/search_form.html')
            )
)


class SearchQuery(views.View):
    isplugin = True
    def __init__(self, in_navigation = 0, astable = True, **kwargs):
        super(SearchQuery,self).__init__(in_navigation=in_navigation,
                                        astable=astable,
                                        **kwargs)
        
    def render(self, djp):
        return self.get_form(djp).render(djp)


class SearchView(SearchQuery):    
    @property
    def engine(self):
        return self.appmodel.engine    
    
    def appquery(self, djp):
        '''This function implements the search query.
The query is build using the search fields specifies in
:attr:`djpcms.views.appsite.ModelApplication.search_fields`.
It returns a queryset.
        '''
        f = self.get_form(djp)
        if f.is_valid():
            q = f.form.cleaned_data['q']
            if q:
                return self.engine.search(q)
    
    def render(self, djp):
        qs = self.appquery(djp)
        return ''
    
    def ajax__autocomplete(self, djp):
        qs = self.appquery(djp)
        params = djp.request.data_dict
        if 'maxRows' in params:
            qs = qs[:int(params['maxRows'])]
        return CustomHeaderBody('autocomplete',
                                list(self.appmodel.gen_autocomplete(qs)))
        
    

class Application(views.Application):
    engine = None
    query = SearchQuery(form = HtmlSearchForm,
                        form_method = 'GET',
                        form_ajax = False,
                        description = 'Seach Form')
    search = SearchView(regex = 'search-results',
                        form = HtmlSearchForm,
                        form_method = 'GET',
                        description = 'Search Results')
    
    def __init__(self,*args,**kwargs):
        self.engine = kwargs.pop('engine',None) or self.engine
        super(Application,self).__init__(*args,**kwargs)


    

