import functools


__all__ = ['memoized',
           'LazyMethod',
           'lazymethod',
           'lazyproperty']


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


class LazyMethod(object):

    def __init__(self, safe=False, as_property=False):
        self.safe = safe
        self.as_property = as_property

    def __call__(self, f):
        '''Decorator which can be used on a member function
to store the result for futures uses.'''
        name = '_lazy_%s' % f.__name__

        def _(obj, *args, **kwargs):
            if not hasattr(obj, name):
                try:
                    value = f(obj, *args, **kwargs)
                except:
                    if self.safe:
                        return None
                    else:
                        raise
                setattr(obj, name, value)
                if is_async(value):
                    value.add_callback(
                            lambda r: self._store_value(obj, name, r))
                    if self.safe:
                        value.add_errback(
                            lambda r: self._store_value(obj, name, None))
            return getattr(obj, name)

        _.__doc__ = f.__doc__
        _.__name__ = f.__name__

        if self.as_property:
            _ = property(_)

        return _

    def _store_value(self, obj, name, value):
        setattr(obj, name, value)
        return value


def lazymethod(f):
    return LazyMethod(False,False)(f)

def lazyproperty(f):
    return LazyMethod(False,True)(f)

