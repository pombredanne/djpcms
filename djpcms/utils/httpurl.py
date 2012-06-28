'''Use pulsar httpurl and multiform'''
from pulsar.utils.httpurl import *
from pulsar.utils.multipart import parse_form_data

from .structures import MultiValueDict


class QueryDict(MultiValueDict):
    
    def __init__(self, query_string, encoding = 'utf-8'):
        super(QueryDict,self).__init__()
        self.encoding = encoding
        # keep_blank_values=True
        for key, value in parse_qsl((query_string or ''), True):
            self[to_string(key, encoding, errors='replace')] =\
                            to_string(value, encoding, errors='replace')
                            
                            
def query_from_string(val):
    '''Conver a string into a parameters for a queryset.'''
    r = {}
    if val:
        try:
            q = QueryDict(val)
            return query_from_querydict(q)
        except:
            return r
    return r

def query_from_querydict(q):
    r = {}
    for k,v in q.lists():
        if len(v) > 1:
            k = '{0}__in'.format(k)
        else:
            v = v[0]
        r[k] = v
    return r

def remove_end_slashes(url):
    if url.endswith('/'):
        url = url[:-1]
    if url.startswith('/'):
        url = url[1:]
    return url

def urlbits(url):
    url = remove_end_slashes(url)
    return url.split('/')

def urlfrombits(bits):
    if bits:
        return '/%s/' % '/'.join(bits)
    else:
        return '/'