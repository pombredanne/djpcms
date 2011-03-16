from stdnet import orm
from stdnet.utils import to_string


class RedisServer(orm.StdModel):
    host = orm.CharField(default = 'localhost')
    port = orm.IntegerField(default = 6379, index = False)
    notes = orm.CharField(required = False)
    
    def __unicode__(self):
        return to_string('{0}:{1}'.format(self.host,self.port))