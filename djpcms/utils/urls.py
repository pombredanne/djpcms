import re

from py2py3 import ispy3k, map, to_string, native_str


__all__ = ['urlparse',
           'urlencode',
           'urlbits',
           'urlfrombits',
           'urlquote',
           'parentpath',
           'closedurl',
           'openedurl',
           'routejoin',
           'iri_to_uri',
           'remove_double_slash',
           'URI_RESERVED']


if ispy3k:
    from urllib.parse import urlparse, unquote, urlsplit, quote, urlencode,\
                                urlunparse
else:
    from urlparse import urlparse, unquote, urlsplit, urlunparse
    from urllib import urlencode, quote
    
urlquote = quote

URI_RESERVED = set((';','/','?',':','@','&','=','+','$',','))
#: list of characters that are always safe in URLs.
_always_safe = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                'abcdefghijklmnopqrstuvwxyz'
                '0123456789_.-')
_safe_map = dict((c, c) for c in _always_safe)
for i in range(0x80):
    c = chr(i)
    if c not in _safe_map:
        _safe_map[c] = '%%%02X' % i
_safe_map.update((chr(i), '%%%02X' % i) for i in range(0x80, 0x100))
_safemaps = {}

#: lookup table for encoded characters.
_hexdig = '0123456789ABCDEFabcdef'
_hextochr = dict((a + b, chr(int(a + b, 16)))
                 for a in _hexdig for b in _hexdig)


def urlbits(url):
    if url.endswith('/'):
        url = url[:-1]
    if url.startswith('/'):
        url = url[1:]
    return url.split('/')


def urlfrombits(bits):
    if bits:
        return '/%s/' % '/'.join(bits)
    else:
        return '/'


def remove_double_slash(route):
    if '//' in route:
        route = re.sub('/+', '/', route)
    return route


def closedurl(url):
    '''Close a url with SLASHes::
    
    >>> closedurl('bla')
    >>> '/bla/'
    >>> closedurl('/bla')
    >>> '/bla/'
    '''
    url = remove_double_slash(url)
    if not url.endswith('/'):
        url += '/'
    if not url.startswith('/'):
        url = '/' + url
    return url


def openedurl(url):
    url = remove_double_slash(url)
    if url.endswith('/'):
        url = url[:-1]
    if url.startswith('/'):
        url = url[1:]
    return url

def routejoin(*routes):
    route = '/'.join(routes)
    return remove_double_slash(route)


def parentpath(url):
    slash = '/'
    s = urlparse(url)
    bits = s.path.split(slash)
    c = 0
    for bit in reversed(bits):
        c += 1
        if bit:
            break
    bits = bits[:-c]
    if bits:
        path = slash.join(bits)
        if not path:
            path = slash
        elif path[-1] != slash:
            path += slash
        s = list(s)
        s[2] = path
        s[3] = s[4] = s[5] = ''
        return urlunparse(s)
    else:
        return None
    
    
def _urlquote(s, safe='/'):
    s = to_string(s)
    if not s or not s.rstrip(_always_safe + safe):
        return s
    try:
        quoter = _safemaps[safe]
    except KeyError:
        safe_map = _safe_map.copy()
        safe_map.update([(c, c) for c in safe])
        _safemaps[safe] = quoter = safe_map.__getitem__
    return _join(map(quoter, s))


def iri_to_uri(iri, kwargs = None):
    """Convert an Internationalized Resource Identifier (IRI) portion to a URI
    portion that is suitable for inclusion in a URL.

    This is the algorithm from section 3.1 of RFC 3987.  However, since we are
    assuming input is either UTF-8 or unicode already, we can simplify things a
    little from the full method.

    Returns an ASCII string containing the encoded result.
    """
    # The list of safe characters here is constructed from the "reserved" and
    # "unreserved" characters specified in sections 2.2 and 2.3 of RFC 3986:
    #     reserved    = gen-delims / sub-delims
    #     gen-delims  = ":" / "/" / "?" / "#" / "[" / "]" / "@"
    #     sub-delims  = "!" / "$" / "&" / "'" / "(" / ")"
    #                   / "*" / "+" / "," / ";" / "="
    #     unreserved  = ALPHA / DIGIT / "-" / "." / "_" / "~"
    # Of the unreserved characters, urllib.quote already considers all but
    # the ~ safe.
    # The % character is also added to the list of safe characters here, as the
    # end of section 3.1 of RFC 3987 specifically mentions that % must not be
    # converted.
    if iri is None:
        return iri
    if kwargs:
        iri = '{0}?{1}'.format(iri,'&'.join(('{0}={1}'.format(k,v) for k,v in kwargs.items())))
    return urlquote(native_str(iri), safe="/#%[]=:;$&()+,!?*@'~")
