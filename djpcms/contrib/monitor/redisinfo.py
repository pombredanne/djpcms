from distutils.version import StrictVersion
from datetime import datetime, timedelta

from djpcms import forms
from djpcms.utils.collections import OrderedDict

from stdnet.utils.format import format_number


class RedisServerForm(forms.Form):
    host = forms.CharField(initial = 'localhost')
    port = forms.IntegerField(initial = 6379)
    notes = forms.CharField(widget = forms.TextArea)


def niceadd(l,name,value):
    if value is not None:
        l.append({'name':name,'value':value})


def nicedate(t):
    try:
        from django.conf import settings
        d = datetime.fromtimestamp(t)
        return '%s %s' % (format(d.date(),settings.DATE_FORMAT),
                          time_format(d.time(),settings.TIME_FORMAT)) 
    except:
        return ''

    
fudge  = 1.25
hour   = 60.0 * 60.0
day    = hour * 24.0
week   = 7.0 * day
month  = 30.0 * day
def nicetimedelta(t):
    tdelta = timedelta(seconds = t)
    days    = tdelta.days
    sdays   = day * days
    delta   = tdelta.seconds + sdays
    if delta < fudge:
        return 'about a second'
    elif delta < (60.0 / fudge):
        return 'about %d seconds' % int(delta)
    elif delta < (60.0 * fudge):
        return 'about a minute'
    elif delta < (hour / fudge):
        return 'about %d minutes' % int(delta / 60.0)
    elif delta < (hour * fudge):
        return 'about an hour'
    elif delta < day:
        return 'about %d hours' % int(delta / hour)
    elif days == 1:
        return 'about 1 day'
    else:
        return 'about %s days' % days


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


class RedisInfo(object):
    
    def __init__(self, version, info, path):
        self.version = version
        self.info = info
        self.panels = OrderedDict()
        self.path = path
        self.fill()
        
    def _dbs(self):
        info = self.info
        for k in info:
            if k[:2] == 'db':
                try:
                    n = int(k[2:])
                except:
                    continue
                else:
                    yield k,n,info[k]
    
    def dbs(self):
        return sorted(self._dbs(), key = lambda x : x[1])
            
    def db(self,n):
        return self.info['db{0}'.format(n)]
    
    def keys(self):
        tot = 0
        path = self.path
        databases = []
        for k,n,data in self.dbs():
            keydb = data['keys']
            url = '{0}{1}/'.format(path,n)
            link = '<a href="{0}" title="database {1}">{2}</a>'.format(url,n,k)
            flush = '<a href="{0}flush/" title="flush database {1}">flush</a>'.format(url,n,k)
            databases.append((link,keydb,data['expires'],flush))
            tot += keydb
        self.panels['keys'] = {'headers':('db','keys','expires','actions'),
                               'data': databases}
        return tot
            
    def fill(self):
        info = self.info
        server = self.panels['Server'] = []
        keys = self.keys()
        niceadd(server, 'Redis version', self.version)
        niceadd(server, 'Process id', info['process_id'])
        niceadd(server, 'Total keys', format_number(keys))
        niceadd(server, 'Memory used', info['used_memory_human'])
        niceadd(server, 'Up time', nicetimedelta(info['uptime_in_seconds']))
        niceadd(server, 'Append Only File', 'yes' if info.get('aof_enabled',False) else 'no')
        niceadd(server, 'Virtual Memory enabled', 'yes' if info['vm_enabled'] else 'no')
        niceadd(server, 'Last save', nicedate(info['last_save_time']))
        niceadd(server, 'Commands processed', format_number(info['total_commands_processed']))
        niceadd(server, 'Connections received', format_number(info['total_connections_received']))
    

class RedisInfo22(RedisInfo):
    
    def _dbs(self):
        return iteritems(self.info['Keyspace'])
                
    def db(self,n):
        return self.info['Keyspace']['db{0}'.format(n)]
    
    def fill(self, info1, keys):
        info = self.info
        server = info['Server']
        memory = info['Memory']
        disk = info['Diskstore']
        persistence = info['Persistence']
        stats = info['Stats']
        niceadd(info1, 'Redis version', self.version)
        niceadd(info1, 'Process id', server['process_id'])
        niceadd(info1, 'Up time', nicetimedelta(server['uptime_in_seconds']))
        niceadd(info1, 'Total keys', format_number(keys))
        niceadd(info1, 'Memory used', memory['used_memory_human'])
        niceadd(info1, 'Memory fragmentation ratio', memory['mem_fragmentation_ratio'])
        niceadd(info1, 'Diskstore enabled', 'yes' if disk['ds_enabled'] else 'no')
        niceadd(info1, 'Last save', nicedate(persistence['last_save_time']))
        niceadd(info1, 'Commands processed', format_number(stats['total_commands_processed']))
        niceadd(info1, 'Connections received', format_number(stats['total_connections_received']))
            
            
def redis_info(info,path):
    version = get_version(info)
    if StrictVersion(version) >= StrictVersion('2.2.0'):
        return RedisInfo22(version,info,path).panels
    else:
        return RedisInfo(version,info,path).panels
    