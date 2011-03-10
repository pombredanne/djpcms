import copy

from djpcms.core.exceptions import ApplicationUrlException
from djpcms.utils.strings import force_str

try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote


def iri_to_uri(iri):
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
    return quote(force_str(iri), safe="/#%[]=:;$&()+,!?*@'~")


class RegExUrl(object):
    '''Helper class for url regular expression manipulation
    
    .. attribute: url
    
        regular expression string
        
    .. attribute: split
        
        if True the url will be split using '/' as separator  
    '''
    def __init__(self, url = None, split = True, append_slash = True):
        self.url    = str(url or '')
        self.purl   = ''
        self.targs  = 0
        self.nargs  = 0
        self._split = split
        self.breadcrumbs = []
        self.names = []
        self.append_slash = append_slash
        if self.url:
            self.__process()
            if self.append_slash:
                self.url  = '%s/' % self.url
        
    def __len__(self):
        return len(self.url)
    
    def __eq__(self, other):
        if isinstance(other,self.__class__):
            return self.url == other.url
        else:
            return False
    
    def split(self):
        if self._split:
            return self.url.split('/')
        else:
            return ['%s' % self.url]
        
    def __str__(self):
        if self.append_slash:
            return '^%s$' % self.url
        else:
            return self.url

    def get_url(self, **kwargs):
        if kwargs:
            return iri_to_uri(self.purl % kwargs)
        else:
            if self.names:
                raise ApplicationUrlException('Missing key-value\
 arguments for {0} regex'.format(self.purl))
            return self.purl
    
    def __process(self):
        bits = self.split()
        for bit in bits:
            if not bit:
                continue
            if bit.startswith('('):
                self.targs += 1
                st = bit.find('<') + 1
                en = bit.find('>')
                if st and en:
                    name = bit[st:en]
                else:
                    raise ApplicationUrlException('Regular expression for urls requires a keyworld. %s does not have one.' % bit)             
                bit  = '%(' + name + ')s'
                self.names.append(name)
            self.breadcrumbs.append(bit)
            self.purl  += '%s/' % bit

    def __add__(self, other):
        if not isinstance(other,self.__class__):
            raise ValueError
        res = copy.deepcopy(self)
        res.url  = '%s%s' % (res.url,other.url)
        res.purl = '%s%s' % (res.purl,other.purl)
        res.targs += other.targs
        res.nargs += other.nargs
        res.names.extend(other.names)
        return res
        
        