from djpcms.cms import Http404
from djpcms import views

class PassView(views.View):
    
    def __call__(self, request):
        raise Http404()


class PassThrough(views.Application):
    '''The passthough application allows its children to be displayed
at the top level of the current page navigation.'''
    home = PassView()