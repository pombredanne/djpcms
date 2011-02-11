
from djpcms.views import appsite, appview

from .forms import ShortPageForm


class editPageView(appview.EditView):
    pass
        
    

class PageApplication(appsite.ModelApplication):
    '''Application for inline editing of pages'''
    form  = ShortPageForm
    
    main = appview.SearchView()
    changeroot = editPageView(regex = 'route', parent = 'main')
    change = editPageView(regex = '(?P<path>[\w./-]*)', splitregex = False,
                          parent = 'changeroot')
    
    def get_object(self, request, **kwargs):
        url = '/'
        if 'path' in kwargs:
            url += kwargs['path']
        return self.mapper.get(url = url)
        
    def objectbits(self, page):
        return {'path': page.url[1:]}
    