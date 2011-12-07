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


class aList(list):
    pass

class aDict(dict):
    pass


class AsyncResponse(object):
    __slots__ = ('handler','response','callback','loops','async')
    def __init__(self, handler, response, callback):
        self.handler = handler
        self.response = response
        self.callback = callback
        _process = self._process
        check_async = handler.check_async
        self.loops = 0
        self.async = lambda v : check_async(_process(v))
        
    def __iter__(self):
        yield self.handler.not_done_yet()
        yield self.run()
        
    def run(self):
        '''Run the asynchronous response. If all resulats are available
 it return the result otherwise it return ``self``.'''
        self.loops += 1
        async, result = self.async(self.response)
        if async:
            return self
        elif self.callback:
            return self.callback(result)
        else:
            return result
    
    def _process(self, value):
        '''Recursive function for handling asynchronous content
        '''
        async = self.async
        if isinstance(value,dict) and not isinstance(value,aDict):
            new_value = aDict()
            for k,val in iteritems(value):
                is_async,val = async(val)
                if is_async:
                    return val
                else:
                    new_value[k] = val
            return new_value
        #
        elif isinstance(value, ContextRenderer):
            is_async,val = async(value.context)
            if is_async:
                return val
            else:
                value.context = val
                return value.render()
        #
        elif isinstance(value, (list,tuple)) and not isinstance(value,aList):
            new_value = aList()
            for val in value:
                is_async,val = async(val)
                if is_async:
                    return val
                else:
                    new_value.append(val)
            return new_value
        #
        elif isinstance(value,AsyncResponse):
            return value.run()

        return value


class ResponseHandler(object):
    
    def __call__(self, response, callback = None):
        return AsyncResponse(self,response,callback).run()
        
    def not_done_yet(self):
        '''This function should return an element recognized by the
 asynchronous engine and which causes the engine to continue evaluating
 other requests.
 '''
        raise NotImplementedError('Cannot handle Asynchronous responses')
    
    def check_async(self, value):
        if isinstance(value,AsyncResponse):
            return True,value
        else:
            return self.async(value)
        
    def async(self, value):
        '''Check if *value* is an asynchronous element. It returns a two
 elements tuple containing a boolean flag and a result. If *value* is
 asynchronous and its result is not yet available, the function should return::
     
     (True,newvalue)
     
 otherwise::
 
     (False,newvalue)
     
 where *newvalue* can be *value* or a modified version.
 
 This function should be implemented by asynchronous engines.'''
        if hasattr(value,'query'):
            value = value.query
        return False,value
    
