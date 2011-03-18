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


def redistable():
    return {'set':{'count':0,'size':0},
            'zset':{'count':0,'size':0},
            'list':{'count':0,'size':0},
            'hash':{'count':0,'size':0},
            'ts':{'count':0,'size':0},
            'string':{'count':0,'size':0},
            'unknow':{'count':0,'size':0}}

def incr_count(table, t, c, s):
    d = table[t]
    d['count'] += 1
    d['size'] += s


def type_length(r, key, table):
    '''Retrive the type and length of a redis key.
    '''
    pipe = r.pipeline()
    pipe.type(key).ttl(key)
    tt = pipe.execute()
    typ = tt[0]
    if typ == 'set':
        cl = pipe.scard(key).srandmember(key).execute()
        l = cl[0]
        incr_count(table,typ,l,len(cl[1]))       
    elif typ =='zset':
        cl = pipe.zcard(key).zrange(key,0,0).execute()
        l = cl[0]
    elif typ == 'list':
        l = r.llen(key)
    elif typ == 'hash':
        l = r.hlen(key)
    elif typ == 'ts':
        l = r.execute_command('TSLEN', key)
    elif typ == 'string':
        l = r.strlen(key)
    else:
        l = None
    return typ,l,tt[1]
        
        
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
        t = redistable()
        for key in data:
            typ,len,ttl = type_length(r, key, t)
            yield table_checkbox(key),typ,len,ttl
        
        
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
