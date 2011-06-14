from distutils.version import StrictVersion
from datetime import datetime, timedelta

from py2py3 import iteritems

from djpcms import forms, sites
from djpcms.utils.text import nicename
from djpcms.utils.dates import nicetimedelta
from djpcms.utils.structures import OrderedDict
from djpcms.html import icons


def format_int(val):
    def _iter(n):
        n = int(val)
        c = 0
        for v in reversed(str(abs(n))):
            if c == 3:
                c = 0
                yield ','
            else:
                yield v
    n = int(val)
    c = ''.join(reversed(_iter(n)))
    if n < 0:
        c = '-{0}'.format(c)
    return c


class ServerForm(forms.Form):
    host = forms.CharField(initial = 'localhost')
    port = forms.IntegerField(initial = 6379)
    notes = forms.CharField(widget = forms.TextArea, required = False)


def niceadd(l,name,value):
    if value is not None:
        l.append({'name':name,'value':value})


def nicedate(t):
    try:
        d = datetime.fromtimestamp(t)
        return '%s %s' % (format(d.date(),site.settings.DATE_FORMAT),
                          time_format(d.time(),site.settings.TIME_FORMAT)) 
    except:
        return ''
    

def getint(v):
    try:
        return int(v)
    except:
        return None


def get_version(info):
    if 'redis_version' in info:
        return info['redis_version']
    else:
        return info['Server']['redis_version']
    
    
class RedisDbData(object):
    
    def __init__(self, db, data):
        self.db = db
        self.keys = data['keys']
        self.expires = data['expires']
    
    def all(self):
        pass
        
    
class RedisData(list):
    
    def append(self, db, data):
        super(RedisData,self).append(RedisDbData(db,data))
    
    @property
    def totkeys(self):
        keys = 0
        for db in self:
            keys += db.keys
        return keys


class RedisInfo(object):
    
    def __init__(self, version, info, path):
        self.version = version
        self.info = info
        self.path = path
        self._panels = OrderedDict()
        self._processed = False
        self.tot_keys = self.makekeys()
        
    def __get_panels(self):
        if not self._processed:
            self._processed = True
            self.fill()
        return self._panels
    panels = property(__get_panels)
    
    def _dbs(self,keydata):
        for k in keydata:
            if k[:2] == 'db':
                try:
                    n = int(k[2:])
                except:
                    continue
                else:
                    yield k,n,keydata[k]
    
    def dbs(self,keydata):
        return sorted(self._dbs(keydata), key = lambda x : x[1])
            
    def db(self,n):
        return self.info['db{0}'.format(n)]
    
    def keys(self, keydata):
        rd = RedisData()
        tot = 0
        path = self.path
        databases = []
        for k,n,data in self.dbs(keydata):
            keydb = data['keys']
            rd.append(n,data)
            #url = '{0}{1}/'.format(path,n)
            #link = '<a href="{0}" title="database {1}">{2}</a>'.format(url,n,k)
            #databases.append((link,keydb,data['expires']))
            #tot += keydb
        self._panels['keys'] = rd
        #self._panels['keys'] = {'headers':('db','keys','expires'),
        #                       'data': databases}
        return rd.totkeys
            
    def makekeys(self):
        return self.keys(self.info)
            
    def fill(self):
        info = self.info
        server = self._panels['Server'] = []
        niceadd(server, 'Redis version', self.version)
        niceadd(server, 'Process id', info['process_id'])
        niceadd(server, 'Total keys', format_int(self.tot_keys))
        niceadd(server, 'Memory used', info['used_memory_human'])
        niceadd(server, 'Up time', nicetimedelta(info['uptime_in_seconds']))
        niceadd(server, 'Append Only File', 'yes' if info.get('aof_enabled',False) else 'no')
        niceadd(server, 'Virtual Memory enabled', 'yes' if info['vm_enabled'] else 'no')
        niceadd(server, 'Last save', nicedate(info['last_save_time']))
        niceadd(server, 'Commands processed', format_int(info['total_commands_processed']))
        niceadd(server, 'Connections received', format_int(info['total_connections_received']))
    

class RedisInfo22(RedisInfo):
    names = ('Server','Memory','Persistence','Diskstore','Replication','Clients','Stats','CPU')
    
    def makekeys(self):
        return self.keys(self.info['Keyspace'])
        
    def makepanel(self, name):
        pa = self._panels[name] = []
        for k,v in iteritems(self.info[name]):
            if v == 0:
                v = icons.circle_check()
            elif v == 1:
                v = icons.circle_check()
            pa.append({'name':nicename(k),'value':v})
            
    def fill(self):
        info = self.info
        for name in self.names:
            self.makepanel(name)
            
            
def redis_info(info,path):
    version = get_version(info)
    if StrictVersion(version) >= StrictVersion('2.2.0'):
        return RedisInfo22(version,info,path)
    else:
        return RedisInfo(version,info,path)
    