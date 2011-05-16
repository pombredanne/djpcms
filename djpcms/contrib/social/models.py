'''
Django model for linked accounts
'''
from stdnet import orm


class LinkedAccount(orm.StdModel):
    '''Stores authentication token and secret key for a linked account'''
    user       = models.ForeignKey(User, related_name = 'linked_accounts')
    tokendate  = models.DateTimeField()
    uid        = models.CharField(max_length = 3000)
    token      = models.CharField(max_length = 3000)
    secret     = models.CharField(max_length = 3000)
    provider   = models.CharField(blank = False, max_length = 100)
    data       = JSONField()
    
    def __unicode__(self):
        return self.provider



#def clearcookie(sender, instance, **kwargs):
#    provider = instance.get_provider(instance.provider)
    
    
#signals.post_delete.connect(clearcookie, sender=LinkedAccount)