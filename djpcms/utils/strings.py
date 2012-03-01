import sys
import locale
import codecs
from datetime import datetime, date, time
from decimal import Decimal

from .py2py3 import string_type


__all__ = ['nodata',
           'encode_str',
           'force_str',
           'escape',
           'smart_escape',
           'mark_safe']


class nodata(object):
    pass
    
EMPTY = ''
NOTHING = (None,EMPTY,nodata)

protected_types = (int, bool, datetime, date, time, float, Decimal)


class SafeString(string_type):
    __html__ = True

    
def mark_safe(v):
    return SafeString(v)


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


# The encoding of the default system locale but falls back to the
# given fallback encoding if the encoding is unsupported by python or could
# not be determined.  See tickets #10335 and #5846
try:
    DEFAULT_LOCALE_ENCODING = locale.getdefaultlocale()[1] or 'ascii'
    codecs.lookup(DEFAULT_LOCALE_ENCODING)
except:
    DEFAULT_LOCALE_ENCODING = 'ascii'
    

def escape(html):
    """Returns the given HTML with ampersands,
quotes and angle brackets encoded."""
    if hasattr(html,'__html__'):
        return html
    if html in NOTHING:
        return ''
    else:
        return force_str(html).replace('&', '&amp;').replace('<', '&lt;')\
            .replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')


def smart_escape(text):
    if hasattr(text,'__html__'):
        return text
    lines = force_str(text).split('\n')
    if len(lines) > 1:
        r = len(lines)
        return '<textarea rows="{0}" readonly="readonly">{1}</textarea>'.format(r,escape(text))
        #return '<p>{0}</p>'.format('</p><p>'.join((escape(text) for text in lines)))
    else:
        return escape(text)
    