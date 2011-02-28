from datetime import datetime

from stdnet import orm
from stdnet.contrib.sessions.models import User


class Issue(orm.StdModel):
    timestamp = orm.DateTimeField(default = datetime.now)
    user = orm.ForeignKey(User, required = False)
    description = orm.CharField(required = True)
    closed = orm.BooleanField()
    body = orm.CharField()
    
    def __unicode__(self):
        return self.description
