'''Models used by the test suite.
'''
from sessions.models import User
from stdnet import orm
        

class Portfolio(orm.StdModel):
    user = orm.ForeignKey(models.User)
    name = orm.CharField(max_length = 200)
    description = models.TextField()
    
    def __unicode__(self):
        return self.name
    