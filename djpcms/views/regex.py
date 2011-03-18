import copy

from djpcms.core.exceptions import ApplicationUrlException
from djpcms.utils import iri_to_uri, openedurl, SLASH
from djpcms.utils.strings import force_str


__all__ = ['RegExUrl']


class RegExUrl(object):
    '''Helper class for url regular url expression manipulation
    
    .. attribute: url
    
        a url regular expression string
        
    .. attribute: append_slash
    
        if ``True`` the url will have a slash appended at the end.
        If set to ``False`` the url cannot be prepended to other urls
        
        Default ``True``.
    '''
    def __init__(self, url = None, append_slash = True):
        self.url = openedurl(str(url or ''))
        self.purl = ''
        self.targs = 0
        self.nargs = 0
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
        
    def __str__(self):
        if self.append_slash:
            return '^{0}$'.format(self.url)
        else:
            return '^{0}'.format(self.url)

    def get_url(self, **kwargs):
        if kwargs:
            return iri_to_uri(self.purl % kwargs)
        else:
            if self.names:
                raise ApplicationUrlException('Missing key-value\
 arguments for {0} regex'.format(self.purl))
            return self.purl
    
    def __process(self):
        names = []
        front = self.url
        back = ''
        star = '*'
        while front:
            st = front.find('(') + 1
            en = front.find(')')
            if st and en:
                st -= 1
                en += 1
                names.append(front[st:en])
                back += front[:st] + star
                front = front[en:]
            else:
                back += front
                front = None
        
        bits = back.split(SLASH)
        for bit in bits:
            if not bit:
                continue
            if bit == star:
                bit = names.pop(0)
                st = bit.find('<') + 1
                en = bit.find('>')
                if st and en:
                    name = bit[st:en]
                else:
                    raise ApplicationUrlException('Regular expression for urls requires a keyworld. %s does not have one.' % bit) 
                bit  = '%(' + name + ')s'
                self.names.append(name)
            self.breadcrumbs.append(bit)
        self.purl = SLASH.join(self.breadcrumbs)
        if self.append_slash:
            self.purl += SLASH

    def __add__(self, other):
        if not self.append_slash:
            raise ValueError('Cannot prepend to another url. Append slash is set to false')
        cls = self.__class__
        append_slash = True
        if isinstance(other,cls):
            append_slash = other.append_slash
            other = other.url
        else:
            other = str(other)
        return self.__class__(self.url + other,
                              append_slash = append_slash)
        
        