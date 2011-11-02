from datetime import datetime

from stdnet import orm
from stdnet.utils import to_string


class RedisServer(orm.StdModel):
    host = orm.CharField(default = 'localhost')
    port = orm.IntegerField(default = 6379, index = False)
    notes = orm.CharField(required = False)
    
    def __unicode__(self):
        return to_string('{0}:{1}'.format(self.host,self.port))
    
    
class Log(orm.StdModel):
    '''A database log entry'''
    timestamp = orm.DateTimeField(default=datetime.now)
    level = orm.SymbolField()
    msg = orm.CharField()
    source = orm.CharField()
    host = orm.CharField()
    user = orm.SymbolField(required=False)
    client = orm.CharField()

    class Meta:
        ordering = '-timestamp'
        
    def abbrev_msg(self, maxlen=500):
        if len(self.msg) > maxlen:
            return '%s ...' % self.msg[:maxlen]
        return self.msg
    abbrev_msg.short_description = 'abbreviated msg'
        
    