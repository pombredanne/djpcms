
from djpcms.views import appsite, appview

from .forms import ShortPageForm


class editPageView(appview.EditView):
    pass
        
    

class PageApplication(appsite.ModelApplication):
    '''Application for inline editing of pages'''
    form  = ShortPageForm
    
    main = appview.SearchView()
    editroot = editPageView(regex = 'route', parent = 'main')
    edit = editPageView(regex = '(?P<path>[\w./-]*)', splitregex = False, parent = 'editroot')
    
    def get_object(self, request, **kwargs):
        url = '/'
        if 'path' in kwargs:
            url += kwargs['path']
        return self.mapper.get(url = url)
        
    def objectbits(self, page):
        return {'path': page.url[1:]}
    