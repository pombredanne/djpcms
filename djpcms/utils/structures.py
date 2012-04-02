import sys
from copy import copy
from inspect import isgenerator
from collections import *

from .py2py3 import itervalues, iteritems

if sys.version_info < (2,7):    # pragma nocover
    from djpcms.utils.fallbacks._collections import *

    
def aslist(value):
    if isinstance(value,list):
        return value
    if isgenerator(value) or isinstance(value,(tuple,set,frozenset)):
        return list(value)
    else:
        return [value]


class MultiValueDict(dict):
    """A subclass of dictionary customized to handle multiple
values for the same key.
    """
    def __init__(self, data = ()):
        if isinstance(data, dict):
            data = data.items()
        key_to_list_mapping = ((k,aslist(v)) for k,v in data)
        super(MultiValueDict, self).__init__(key_to_list_mapping)

    def __getitem__(self, key):
        """Returns the data value for this key. If the value is a list with
only one element, it returns that element, otherwise it returns the list.
Raises KeyError if key is not found."""
        l = super(MultiValueDict, self).__getitem__(key)
        return l[0] if len(l) == 1 else l

    def __setitem__(self, key, value):
        if key in self:
            l = super(MultiValueDict, self).__getitem__(key)
            l.append(value)
        else:
            super(MultiValueDict, self).__setitem__(key, [value])
            
    def update(self, items):
        if isinstance(items, dict):
            items = iteritems(items)
        for k,v in items:
            self[k] = v

    def __copy__(self):
        return self.__class__(((k, v[:]) for k, v in self.lists()))

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def getlist(self, key):
        """Returns the list of values for the passed key."""
        return super(MultiValueDict, self).__getitem__(key)
    
    def setlist(self, key, _list):
        if key in self:
            self.getlist(key).extend(_list)
        else:
            _list = aslist(_list)
            super(MultiValueDict, self).__setitem__(key, _list)

    def setdefault(self, key, default=None):
        if key not in self:
            self[key] = default
        return self[key]

    def items(self):
        """Returns a generator ovr (key, value) pairs,
where value is the last item in the list associated with the key.
        """
        return ((key, self[key]) for key in self)

    def lists(self):
        """Returns a list of (key, list) pairs."""
        return super(MultiValueDict, self).items()

    def values(self):
        """Returns a list of the last value on every key list."""
        return [self[key] for key in self.keys()]

    def copy(self):
        return copy(self)