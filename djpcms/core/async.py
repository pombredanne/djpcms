from py2py3 import iteritems

from djpcms.html import ContextRenderer


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


def default_response_handler(site, data, callback = None):
    if isinstance(data,dict):
        rr = default_response_handler
        data = dict(((k,rr(site,v)) for k,v in iteritems(data)))
    elif isinstance(data,ContextRenderer):
        data = data.render()
    elif hasattr(data,'query'):
        data = data.query
    return callback(data) if callback else data
