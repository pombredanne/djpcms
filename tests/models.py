__test__ = False
import os

if os.environ['stdcms']:
    from stdcms.sessions import User
    from stdnet import odm
    
    class Portfolio(odm.StdModel):
        user = odm.ForeignKey(User)
        name = odm.CharField(max_length=200)
        description = odm.CharField()
        
        def __unicode__(self):
            return self.name
        
        
    class Book(odm.StdModel):
        title = odm.CharField()
        author = odm.CharField()
        year = odm.IntegerField()
        description = odm.CharField()
        
        def __unicode__(self):
            return self.title
        