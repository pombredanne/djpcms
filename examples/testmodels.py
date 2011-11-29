'''Models used by the test suite.
'''
from sessions.models import User
from stdnet import orm
        

class Portfolio(orm.StdModel):
    user = orm.ForeignKey(User)
    name = orm.CharField(max_length = 200)
    description = orm.CharField()
    
    def __unicode__(self):
        return self.name
    