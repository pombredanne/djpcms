from stdnet.orm.query import Manager

from django.core.exceptions import ObjectDoesNotExist


class LinkedManager(Manager):
    '''Manager which will replace the standard manager for stdnet models
linked with django models.'''
    def __init__(self,djmodel,model):
        self.djmodel = djmodel
        self._setmodel(model)
        self.dj      = djmodel.objects
        
    def _get(self, **kwargs):
        return super(LinkedManager,self).get(**kwargs)
        
    def get(self, **kwargs):
        try:
            return self._get(**kwargs)
        except self.model.DoesNotExist:
            pass
        try:
            dobj = self.djmodel.objects.get(**kwargs)
        except ObjectDoesNotExist:
            raise self.model.DoesNotExist
        return self.update_from_django(dobj)
        
    def update_from_django(self, dobj, instance = None):
        if instance is None:
            instance = self.model(id = dobj.id)
        for field in instance._meta.scalarfields:
            name = field.name
            if name is not 'djobject':
                val = getattr(dobj,name,None)
                if val is not None:
                    setattr(instance,name,val)
        instance.djobject = dobj
        instance.save()
        logger.debug('Updated linked stdmodel %s' % instance)
        return instance
        
    def sync(self):
        all = self.all()
        for obj in self.dj.all():
            if not id in all: 
                pass
