
from djpcms.views import appsite, appview

from .forms import ShortPageForm


class editPageView(appview.EditView):
    
    def render(self, djp):
        
    

class PageApplication(appsite.ModelApplication):
    '''Application for inline editing of pages'''
    form  = ShortPageForm
    
    main = appview.SearchView()
    edit = editPageView(regex = '?(<path>.*)', parent = 'main')