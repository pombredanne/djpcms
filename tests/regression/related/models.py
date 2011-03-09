from regression import models


class Holder(models.Model):
    name = models.CharField()
    
    
class Item(models.Model):
    holder = models.ForeignKey(Holder, related_name = 'items')
    name = models.CharField()
