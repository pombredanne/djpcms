
__all__ = ['Promise','async_instance','default_response_handler']


class Promise(object):
    __slots__ = ('request','callback')
    
    def __init__(self, request, callback):
        self.request = request
        self.callback = callback
        
    def __call__(self, result):
        return self.callback(self.request,result)
    

'''wait for an asynchronous instance'''
class async_instance_callback(object):
    __slots__ = ('callable','obj','request','args','kwargs')
    
    def __init__(self, callable, obj, request, *args, **kwargs):
        self.callable = callable
        self.obj = obj
        self.request = request
        self.args = args
        self.kwargs = kwargs
    
    def __call__(self, result):
        request = self.request.for_view_args(instance = result)
        return self.callable(self.obj,request,*self.args,**self.kwargs)


def async_instance(mf):
    
    def _(self, request, *args, **kwargs):
        instance = request.instance
        if not instance or isinstance(instance,self.model):
            return mf(self, request, *args, **kwargs)
        else:
            cbk = async_instance_callback(mf,self,request,*args,**kwargs)
            return request.view.response_handler(request, instance,
                                                 callback = cbk)
    
    return _


def default_response_handler(request, response, callback = None):
    if isinstance(response,dict):
        rr = default_response_handler
        response = dict(((k,rr(request,v)) for k,v in iteritems(response)))
    elif isinstance(response,html.ContextRenderer):
        response = response.render()
    elif hasattr(response,'query'):
        response = response.query
    return callback(response) if callback else response