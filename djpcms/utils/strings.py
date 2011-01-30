import sys
from datetime import datetime, date, time
from decimal import Decimal

from py2py3 import string_type

__all__ = ['UnicodeMixin',
           'encode_str',
           'force_str']


protected_types = (int, datetime, date, time, float, Decimal)


class UnicodeMixin(object):
    """
    A class whose __str__ returns its __unicode__ as a UTF-8 bytestring.

    Useful as a mix-in.
    """
    if sys.version_info[0] >= 3:
        __str__ = lambda x: x.__unicode__()
    else:
        __str__ = lambda x: unicode(x).encode('utf-8')


def encode_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    """Returns a bytestring version of 's',
encoded as specified in 'encoding'.
If strings_only is True, don't convert (some)
non-string-like objects."""
    if isinstance(s,bytes):
        if encoding != 'utf-8':
            return s.decode('utf-8', errors).encode(encoding, errors)
        else:
            return s
        
    if strings_only and (s is None or isinstance(s, protected_types)):
        return s
        
    if not isinstance(s, string_type):
        s = string_type(s)
    
    return s.encode(encoding, errors)
    
    
def force_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Similar to encode_str, except that lazy instances are resolved to
    strings, rather than kept as lazy objects.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    if isinstance(s, string_type):
        return s
    if strings_only and (s is None or isinstance(s, protected_types)):
        return s
    if isinstance(s,bytes):
        return s.decode(encoding,errors)
    return string_type(s)


