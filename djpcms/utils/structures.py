import sys
from copy import copy
from collections import *

if sys.version_info < (2,7):
    from djpcms.utils.fallbacks._collections import *


class MultiValueDict(dict):
    """
    A subclass of dictionary customized to handle multiple values for the
    same key.
    This class exists to solve the irritating problem raised by cgi.parse_qs,
    which returns a list for every key, even though most Web forms submit
    single name-value pairs.
    """
    def __init__(self, key_to_list_mapping=()):
        super(MultiValueDict, self).__init__(key_to_list_mapping)

    def __getitem__(self, key):
        """
        Returns the last data value for this key, or [] if it's an empty list;
        raises KeyError if not found.
        """
        list_ = super(MultiValueDict, self).__getitem__(key)
        try:
            return list_[-1]
        except IndexError:
            return []

    def __setitem__(self, key, value):
        super(MultiValueDict, self).__setitem__(key, [value])

    def __copy__(self):
        return self.__class__(((k, v[:]) for k, v in self.lists()))

    def get(self, key, default=None):
        """
        Returns the last data value for the passed key. If key doesn't exist
        or value is an empty list, then default is returned.
        """
        try:
            val = self[key]
        except KeyError:
            return default
        if val == []:
            return default
        return val

    def getlist(self, key):
        """
        Returns the list of values for the passed key. If key doesn't exist,
        then an empty list is returned.
        """
        try:
            return super(MultiValueDict, self).__getitem__(key)
        except KeyError:
            return []

    def setlist(self, key, list_):
        super(MultiValueDict, self).__setitem__(key, list_)

    def setdefault(self, key, default=None):
        if key not in self:
            self[key] = default
        return self[key]

    def appendlist(self, key, value):
        """Appends an item to the internal list associated with key."""
        if key not in self:
            li = []
            self.setlist(key, li)
        else:
            li = self[key]
        li.append(value)

    def items(self):
        """Returns a generator ovr (key, value) pairs, where value is the last item in
        the list associated with the key.
        """
        return ((key, self[key]) for key in self)

    def lists(self):
        """Returns a list of (key, list) pairs."""
        return super(MultiValueDict, self).items()

    def values(self):
        """Returns a list of the last value on every key list."""
        return [self[key] for key in self.keys()]

    def copy(self):
        """Returns a shallow copy of this object."""
        return copy(self)

