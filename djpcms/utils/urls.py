from py2py3 import ispy3k, urlparse, map, to_string

__all__ = ['urlparse',
           'urlbits',
           'urlfrombits',
           'urlquote',
           'parentpath',
           'SLASH']

if ispy3k:
    urlquote = urlparse.quote
else:
    from urllib import quote as urlquote


SLASH = '/'
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


def parentpath(url):
    s = urlparse.urlparse(url)
    bits = s.path.split(SLASH)
    c = 0
    for bit in reversed(bits):
        c += 1
        if bit:
            break
    bits = bits[:-c]
    if bits:
        path = SLASH.join(bits)
        if not path:
            path = SLASH
        elif path[-1] != SLASH:
            path += SLASH
        s = list(s)
        s[2] = path
        s[3] = s[4] = s[5] = ''
        return urlparse.urlunparse(s)
    else:
        return None
    
    
def _urlquote(s, safe=SLASH):
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
