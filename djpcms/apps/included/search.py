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

class SearchView(views.View):
    search_text = 'q'
    def __init__(self, in_navigation = 0, astable = True,
                 search_text = None, isplugin = True,
                 **kwargs):
        self.search_text = search_text or self.search_text
        super(SearchView,self).__init__(in_navigation=in_navigation,
                                        astable=astable,
                                        isplugin = isplugin,
                                        **kwargs)
    
    @property
    def engine(self):
        return self.appmodel.engine    
    
    def appquery(self, djp):
        '''This function implements the search query.
The query is build using the search fields specifies in
:attr:`djpcms.views.appsite.ModelApplication.search_fields`.
It returns a queryset.
        '''
        request = djp.request
        search_string = request.REQUEST.get(self.search_text,None)
        if search_string:
            
            qs = appmodel.mapper.search_text(qs, search_string, slist)    
        return qs
    
    def render(self, djp):
        return self.get_form(djp).render(djp)
    
    def ajax__autocomplete(self, djp):
        qs = self.appquery(djp)
        params = djp.request.data_dict
        if 'maxRows' in params:
            qs = qs[:int(params['maxRows'])]
        return CustomHeaderBody('autocomplete',
                                list(self.appmodel.gen_autocomplete(qs)))
        
    

class Application(views.Application):
    engine = None
    search = SearchView(form = HtmlSearchForm)
    
    def __init__(self,*args,**kwargs):
        self.engine = kwargs.pop('engine',None) or self.engine
        super(Application,self).__init__(*args,**kwargs)


    

