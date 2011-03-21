from regression import models


class Strategy(models.Model):
    name     = models.CharField(max_length = 200)
    description = models.TextField()
    
    def __unicode__(self):
        return u'%s' % self.name
    
    
class Trade(models.Model):
    name = models.CharField(unique = True, max_length = 200)
    currency = models.CharField(max_length = 3)
    
    
class StrategyTrade(models.Model):
    strategy   = models.ForeignKey(Strategy, related_name = 'wines')
    trade      = models.ForeignKey(Trade, related_name = 'grapes')
    percentage = models.FloatField(default = 1)