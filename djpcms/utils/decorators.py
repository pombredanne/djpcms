import functools


__all__ = ['memoized','storegenarator','lazyattr','lazymethod','lazyproperty']


class memoized(object):
    """Decorator that caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}
      
    def __call__(self, *args, **kwargs):
        try:
            return self.cache[args]
        except KeyError:
            value = self.func(*args)
            self.cache[args] = value
            return value
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.func(*args)
        
    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__
    
    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)
    
    
def storegenarator(f):
    '''Decorator which can be used on a member function
returning a generator. It stores the generated results for future use.
    '''
    name = '_generated_%s' % f.__name__
    def _(self, *args, **kwargs):
        if not hasattr(self,name):
            items = []
            setattr(self,name,items)
            append = items.append
            for g in f(self, *args, **kwargs):
                append(g)
                yield g
        else:
            for g in getattr(self,name):
                yield g
                
    _.__doc__ = f.__doc__
    
    return _


class lazymethod(object):
    
    def __init__(self, safe = False, as_property = False):
        self.safe = safe
        self.as_property = as_property
        
    def __call__(self, f):
        '''Decorator which can be used on a member function.
    It stores the result for futures uses.
        '''
        name = '_lazy_%s' % f.__name__
        
        def _(obj, *args, **kwargs):
            if not hasattr(obj,name):
                try:
                    v = f(obj, *args, **kwargs)
                except:
                    if self.safe:
                        return None
                    else:
                        raise
                setattr(obj,name,v)
            return getattr(obj,name)
            
        _.__doc__ = f.__doc__
        _.__name__ = f.__name__
        
        if self.as_property:
            _ = property(_)
            
        return _
    
    
def lazyattr(f):
    return lazymethod()(f)


def lazyproperty(f):
    return lazymethod(False,True)(f)
