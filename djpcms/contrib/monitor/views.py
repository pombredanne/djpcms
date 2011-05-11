from urllib import urlencode
from datetime import datetime, timedelta
from distutils.version import StrictVersion

from py2py3 import iteritems

from stdnet.lib.redisinfo import RedisStats

from djpcms import forms
from djpcms.html import Paginator, table_checkbox
from djpcms.utils.ajax import jhtmls, jredirect
from djpcms.utils import lazyattr, gen_unique_id
from djpcms.template import loader
from djpcms.views import *

from stdnet.orm import model_iterator
        
        
class DbQuery(object):
    
    def __init__(self, djp, r):
        self.djp   = djp
        self.r     = RedisStats(r)
        
    def __len__(self):
        return self.r.size()
    
    def __iter__(self):
        return self.data()
    
    @lazyattr
    def data(self):
        return self.r.keys()
    
    def __getitem__(self, slic):
        data = self.data()[slic]
        type_length = self.r.type_length
        for key in data:
            typ,len,ttl = type_length(key)
            yield (table_checkbox(key,key),typ,len,ttl)
        
        
class RedisDbView(ViewView):
    '''Display information about keys in one database.'''
    astable = True
    default_title = 'Database {0[db]}'
    headers = ('key','type','length','time to expiry')
    
    def render(self, djp):
        r = self.appmodel.get_redis(djp.instance, db = djp.kwargs['db'])
        qs = DbQuery(djp,r)
        return self.appmodel.render_query(djp,qs)


class RedisDbFlushView(RedisDbView):
    
    def default_post(self, djp):
        r = self.appmodel.get_redis(djp.instance, db = djp.kwargs['db'])
        keys = len(r.keys())
        return jhtmls(identifier = 'td.redisdb%s.keys' % r.db,
                      html = keys)


class StdModelDeleteAllView(ModelView):
    _methods = ('post',)
    
    def default_post(self, djp):
        self.model.flush()
        next,curr = forms.next_and_current(djp.request)
        return jredirect(next or curr)
