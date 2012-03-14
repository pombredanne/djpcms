__test__ = False
import os

if os.environ['stdcms']:
    from stdcms.sessions import User
    from stdnet import orm
            
    
    class Portfolio(orm.StdModel):
        user = orm.ForeignKey(User)
        name = orm.CharField(max_length = 200)
        description = orm.CharField()
        
        def __unicode__(self):
            return self.name
        
        
    class Book(orm.StdModel):
        title = orm.CharField()
        author = orm.CharField()
        year = orm.IntegerField()
        description = orm.CharField()
        
        def __unicode__(self):
            return self.title
        