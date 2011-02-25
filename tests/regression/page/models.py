from regression import models


class Strategy(models.Model):
    name     = models.CharField(unique = True, max_length = 200)
    description = models.TextField()
    
    def __unicode__(self):
        return self.name
