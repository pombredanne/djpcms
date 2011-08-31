from regression import models
from djpcms import sites

if models.Model:
        
    class Portfolio(models.Model):
        user = models.ForeignKey(models.User)
        name = models.CharField(max_length = 200)
        description = models.TextField()
        
        def __unicode__(self):
            return self.name
    