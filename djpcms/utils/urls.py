import re

from py2py3 import ispy3k, force_native_str


__all__ = ['urlparse',
           'urlencode',
           'urlbits',
           'urlfrombits',
           'urlquote',
           'urlunquote',
           'parentpath',
           'closedurl',
           'openedurl',
           'routejoin',
           'iri_to_uri',
           'uri_to_iri',
           'remove_double_slash',
           'URI_RESERVED']


if ispy3k:
    from urllib.parse import urlparse, unquote, urlsplit, quote, urlencode,\
                                unquote, urlunparse
else:
    from urlparse import urlparse, unquote, urlsplit, urlunparse
    from urllib import urlencode, quote, unquote
    
urlquote = quote
urlunquote = unquote

URI_RESERVED = frozenset((';','/','?',':','@','&','=','+','$',','))

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
    iri = force_native_str(iri)
    if kwargs:
        iri = '{0}?{1}'.format(iri,'&'.join(('{0}={1}'.format(k,v)\
                                              for k,v in kwargs.items())))
    return urlquote(iri, safe=''.join(URI_RESERVED))


def uri_to_iri(uri):
    return urlunquote(force_native_str(uri))
