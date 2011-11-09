
__all__ = ['async_instance']


'''wait for an asynchronous instance'''
class async_instance_callback(object):
    __slots__ = ('callable','obj','djp','args','kwargs')
    
    def __init__(self, callable, obj, djp, *args, **kwargs):
        self.callable = callable
        self.obj = obj
        self.djp = djp
        self.args = args
        self.kwargs = kwargs
    
    def __call__(self, result):
        self.djp.kwargs['instance'] = result
        return self.callable(self.obj,self.djp,*self.args,**self.kwargs)


def async_instance(mf):
    
    def _(self, djp, *args, **kwargs):
        instance = djp.instance
        if not instance or isinstance(instance,djp.model):
            return mf(self, djp, *args, **kwargs)
        else:
            cbk = async_instance_callback(mf,self,djp,*args,**kwargs)
            return djp.root.unwind_query(instance, callback = cbk)
    
    return _