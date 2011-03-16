from urllib import urlencode
from datetime import datetime, timedelta
from distutils.version import StrictVersion

from py2py3 import iteritems

from djpcms import forms
from djpcms.html import Paginator, table_checkbox
from djpcms.utils.ajax import jhtmls, jredirect
from djpcms.utils import lazyattr, gen_unique_id
from djpcms.template import loader
from djpcms.views import *
        

def type_length(r, key):
    typ = r.type(key)
    l = 1
    if typ == 'set':
        l = r.scard(key)
    elif typ == 'list':
        l = r.llen(key)
    elif typ == 'hash':
        l = r.hlen(key)
    return typ,l
        
        
class DbQuery(object):
    
    def __init__(self, djp, r):
        self.djp   = djp
        self.r     = r
        
    def __len__(self):
        return self.r.dbsize()
    
    def __iter__(self):
        return self.data()
    
    @lazyattr
    def data(self):
        return self.r.keys()
    
    def __getitem__(self, slic):
        data = self.data()[slic]
        r = self.r
        for key in data:
            typ,len = type_length(r, key)
            yield table_checkbox(key),typ,len,r.ttl(key)
        
        
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


class StdModelInformationView(ModelView):
    
    def __init__(self, **kwargs):
        kwargs['isplugin'] = True
        super(StdModelInformationView,self).__init__(**kwargs)
        
    '''Display Information regarding a
    :class:`stdnet.orm.StdModel` registered with a backend database.'''
    def render(self, djp, **kwargs):
        meta = self.model._meta
        return loader.render('monitor/stdmodel.html',{'meta':meta})


class StdModelDeleteAllView(ModelView):
    _methods = ('post',)
    
    def default_post(self, djp):
        self.model.flush()
        next,curr = forms.next_and_current(djp.request)
        return jredirect(next or curr)
