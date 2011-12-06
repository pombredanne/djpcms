from py2py3 import iteritems

from djpcms.html import ContextRenderer


__all__ = ['async_instance', 'ResponseHandler']
   

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


class ResponseHandler(object):
    
    def __call__(self, response, callback = None):
        return self.handle(response, callback)
        
    def release(self, response, callback, nested):
        pass
    
    def async_response(self, response, callback, nested):
        if hasattr(response,'query'):
            response = response.query
        return False,response
    
    def handle(self, response, callback = None, nested = False):
        '''Recursive function for handling asynchronous content
        '''
        if isinstance(response,dict):
            for k,v in list(iteritems(response)):
                v = self.handle(v, nested = True)
                r = self.release(v, callback, nested)
                if r:
                    return r
                else:
                    response[k] = v
        #
        elif isinstance(response, ContextRenderer):
            # we pass the dictionary so the result is either a NOT_DONE or a
            # a new dictionary
            v = self.handle(response.context, nested = True)
            r = self.release(v, callback, nested)
            if r:
                return r
            else:
                response.context = v
                response = response.render()
        #
        elif isinstance(response, (list,tuple)):
            new_response = []
            for v in response:
                v = self.handle(v, nested = True)
                r = self.release(v, callback, nested)
                if r:
                    return r
                else:
                    new_response.append(v)
            response = new_response
        #
        else:
            async,response = self.async_response(response, callback, nested)
            if async:
                return response
        
        return callback(response) if callback else response
