import os
import sys
import time
import types

__all__ = ['string_type',
           'int_type',
           'to_bytestring',
           'to_string',
           'ispy3k',
           'is_string',
           'iteritems',
           'itervalues',
           'zip',
           'map']

def ispy3k():
    return int(sys.version[0]) >= 3


if ispy3k(): # Python 3
    string_type = str
    itervalues = lambda d : d.values()
    iteritems = lambda d : d.items()
    is_string = lambda x : isinstance(x,str)
    int_type = int
    zip = zip
    map = map
        
else: # Python 2
    string_type = unicode
    itervalues = lambda d : d.itervalues()
    iteritems = lambda d : d.iteritems()
    is_string = lambda x : isinstance(x,basestring)
    int_type = (types.IntType, types.LongType)
    from itertools import izip as zip, imap as map
    
    
def to_bytestring(s, encoding='utf-8', errors='strict'):
    """Returns a bytestring version of 's',
encoded as specified in 'encoding'.
If strings_only is True, don't convert (some)
non-string-like objects."""
    if isinstance(s,bytes):
        if encoding != 'utf-8':
            return s.decode('utf-8', errors).encode(encoding, errors)
        else:
            return s
        
    if isinstance(s, string_type):    
        return s.encode(encoding, errors)
    else:
        return s


def to_string(s, encoding='utf-8', errors='strict'):
    """Inverse of to_bytestring"""
    if isinstance(s, string_type):
        return s
    elif isinstance(s,bytes):
        return s.decode(encoding,errors)
    else:
        string_type(s)
    
    
class Platform(object):
    """Gives us information about the platform we're running on"""
    type = os.name
    timer = time.time
    
    def isWindows(self):
        return False
    
    def is7(self):
        return False
    
    def isVista(self):
        return False
    
    def isXP(self):
        return False
    
    def isPosix(self):
        return False
    
    def symlink(self, filename, linkname):
        os.symlink(filename, linkname)


class UnicodeMixin(object):
        
    def __str__(self):
        return '{0} object'.format(self.__class__.__name__)
    
    def __unicode__(self):
        return to_string(str(self))
    