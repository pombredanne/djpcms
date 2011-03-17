from distutils.version import StrictVersion
from datetime import datetime, timedelta

from py2py3 import iteritems

from djpcms import forms
from djpcms.utils.text import nicename
from djpcms.utils.collections import OrderedDict
from djpcms.html import icons

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
        self.makekeys()
        self.fill()
    
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
        tot = 0
        path = self.path
        databases = []
        for k,n,data in self.dbs(keydata):
            keydb = data['keys']
            url = '{0}{1}/'.format(path,n)
            link = '<a href="{0}" title="database {1}">{2}</a>'.format(url,n,k)
            flush = '<a href="{0}flush/" title="flush database {1}">flush</a>'.format(url,n,k)
            databases.append((link,keydb,data['expires'],flush))
            tot += keydb
        self.panels['keys'] = {'headers':('db','keys','expires','actions'),
                               'data': databases}
        return tot
            
    def makekeys(self):
        self.keys(self.info)
            
    def fill(self):
        info = self.info
        server = self.panels['Server'] = []
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
    names = ('Server','Memory','Persistence','Diskstore','Replication','Clients','Stats','CPU')
    
    def makekeys(self):
        self.keys(self.info['Keyspace'])
        
    def makepanel(self, name):
        pa = self.panels[name] = []
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
        #niceadd(server, 'Redis version', self.version)
        #niceadd(server, 'Process id', server['process_id'])
        #niceadd(server, 'Up time', nicetimedelta(server['uptime_in_seconds']))
        #niceadd(memory, 'Total keys', format_number(keys))
        #niceadd(memory, 'Memory used', memory['used_memory_human'])
        #niceadd(memory, 'Memory fragmentation ratio', memory['mem_fragmentation_ratio'])
        #niceadd(server, 'Diskstore enabled', 'yes' if disk['ds_enabled'] else 'no')
        #niceadd(persistence, 'Last save', nicedate(persistence['last_save_time']))
        #niceadd(server, 'Commands processed', format_number(stats['total_commands_processed']))
        #niceadd(server, 'Connections received', format_number(stats['total_connections_received']))
            
            
def redis_info(info,path):
    version = get_version(info)
    if StrictVersion(version) >= StrictVersion('2.2.0'):
        return RedisInfo22(version,info,path).panels
    else:
        return RedisInfo(version,info,path).panels
    