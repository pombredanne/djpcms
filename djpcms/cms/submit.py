

class SubmitMiddleware(object):
    
    def extra_form_data(self, request):
        raise StopIteration()
    
    def check(self, request, data):
        pass
    
    
class SubmitDataMiddleware(object):

    def __init__(self):
        self._middleware = []

    def extra_form_data(self, request):
        '''Generator of name/value pairs for inputs to add to a form.'''
        for middleware in self._middleware:
            for name, value in middleware.extra_form_data(request):
                yield name, value

    def check(self, request, data):
        for middleware in self._middleware:
            middleware(request, data)
            
            
class Referrer(SubmitMiddleware):
    
    def extra_form_data(self, request):
        if request.method == 'GET':
            yield '__referer__', request.path
    
    def check(self, request, data):
        referer = data.get('__referer__')
        if referer:
            pass
    
