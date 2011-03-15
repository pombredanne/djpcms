from stdnet import orm

class UserProfile(orm.StdModel):
    data = orm.JSONField(sep = '_')
    
    def __unicode__(self):
        return self.djobject.__unicode__()