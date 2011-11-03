from djpcms.utils import lazyattr

from stdnet import orm
from stdnet.lib.redisinfo import RedisStats


__all__ = ['DbQuery']


class DbQuery(object):
    
    def __init__(self, djp, r):
        self.djp = djp
        self.r = RedisStats(r)
        
    def __len__(self):
        return self.r.size()
    
    def __iter__(self):
        return self.data().__iter__()
    
    @lazyattr
    def data(self):
        return self.r.keys()
    
    def __getitem__(self, slic):
        data = self.data()[slic]
        type_length = self.r.type_length
        for key in data:
            keys = key.decode()
            typ,len,ttl = type_length(key)
            if ttl == -1:
                ttl = icons.no()
            yield (table_checkbox(keys,keys),typ,len,ttl)

