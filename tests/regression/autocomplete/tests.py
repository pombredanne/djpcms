from djpcms import test, forms
from djpcms.views import appsite, appview

from djpcms.models import SiteContent


class TestForm(forms.Form):
    content = forms.ChoiceField(SiteContent.objects.all)
    
    
class TestFormMulti(forms.Form):
    strategy = forms.MultipleChoiceField(SiteContent.objects.all)


class ApplicationWithAutocomplete(appsite.ModelApplication):
    # RULE 1 the search_fields list
    search_fields = ['code','description']
    # RULE 2 the autocomplete view
    autocomplete = appview.AutocompleteView(regex = 'autocompletetest',
                                            display = 'name')     

# RULE 4 register as usual
appurls = ApplicationWithAutocomplete('/strategies/', SiteContent),
    

class TestAutocomplete(TestCase):
    '''Autocomplete functionalities. Autocomplete widgets are implemented
in :mod:`djpcms.utils.html.autocomplete`.'''

    appurls = 'regression.autocomplete.tests'
        
    def testModelChoiceField(self):
        f = TestForm()
        html = f.as_table()
        self.assertFalse('<select' in html)
        self.assertTrue('href="/strategies/autocompletetest/"' in html)
        
    def testModelMultipleChoiceField(self):
        f = TestFormMulti()
        html = f.as_table()
        self.assertFalse('<select' in html)
        self.assertTrue('href="/strategies/autocompletetest/"' in html)