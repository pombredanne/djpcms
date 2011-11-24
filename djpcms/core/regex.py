import copy

from djpcms import UnicodeMixin, to_string
from djpcms.core.exceptions import ApplicationUrlException
from djpcms.utils import iri_to_uri, openedurl, SLASH
from djpcms.utils.strings import force_str


__all__ = ['Route',
           'RegExUrl',
           'RouteMixin',
           'ALL_URLS',
           'PATH_RE',
           'ALL_REGEX',
           'IDREGEX',
           'UUID_REGEX',
           'SLUG_REGEX']


class RouteMixin(object):

    def route(self):
        raise NotImplementedError
    
    @property
    def path(self):
        return self.route().path


class Route(UnicodeMixin):
    '''Helper class for url regular expressions manipulation
    
.. attribute: url

    a url regular expression string
    
.. attribute: append_slash

    if ``True`` the url will have a slash appended at the end.
    If set to ``False`` the url cannot be prepended to other urls
    
    Default ``False``.
'''
    def __init__(self, url = None, append_slash = False):
        self.__url = openedurl(str(url or ''))
        self.path = ''
        self.targs = 0
        self.nargs = 0
        self.breadcrumbs = []
        self.names = []
        self.append_slash = append_slash
        if self.__url:
            self.__process()
            self.path = SLASH + self.path
        if self.append_slash:
            self.path += SLASH
            if self.__url:
                self.__url += SLASH
    
    def __len__(self):
        return len(self.__url)
    
    def __eq__(self, other):
        if isinstance(other,self.__class__):
            return to_string(self) == to_string(other)
        else:
            return False
        
    def __lt__(self, other):
        if isinstance(other,self.__class__):
            return to_string(self) < to_string(other)
        else:
            raise TypeError('Cannot compare {0} with {1}'.format(self,other))
        
    def __unicode__(self):
        if self.append_slash:
            return to_string('^{0}$'.format(self.__url))
        else:
            return to_string('^{0}'.format(self.__url))

    def get_url(self, **kwargs):
        if kwargs:
            return iri_to_uri(self.path % kwargs)
        else:
            if self.names:
                raise ApplicationUrlException('Missing key-value\
 arguments for {0} regex'.format(self.path))
            return self.path
    
    def __process(self):
        names = []
        front = self.__url
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
                    raise ApplicationUrlException('Regular expression for urls\
 requires a keyworld. %s does not have one.' % bit) 
                bit  = '%(' + name + ')s'
                self.names.append(name)
            self.breadcrumbs.append(bit)
        self.path = SLASH.join(self.breadcrumbs)

    def _get_url(self):
        return self.__url
    
    def __add__(self, other):
        if not self.append_slash:
            raise ValueError('Cannot prepend to another url.\
 Append slash is set to false')
        cls = self.__class__
        append_slash = True
        if isinstance(other,cls):
            append_slash = other.append_slash
            other = other._get_url()
        else:
            other = str(other)
        return self.__class__(self.__url + other,
                              append_slash = append_slash)
        
        
ALL_REGEX = '.*'
PATH_RE = '(?P<path>{0})'.format(ALL_REGEX)
IDREGEX = '(?P<id>\d+)'
SLUG_REGEX = '[-\.\+\#\'\:\w]+'
UUID_REGEX = '(?P<id>[-\w]+)'
ALL_URLS = Route(PATH_RE)

RegExUrl = Route 