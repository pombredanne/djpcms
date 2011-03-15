import logging

from stdnet.orm.query import Manager

from django.core.exceptions import ObjectDoesNotExist

from .utils import LINKED_OBJECT_ATTRIBUTE

logger = logging.getLogger('djpcms.contrib.stdlink')

class LinkedManager(Manager):
    '''Manager which will replace the standard manager for stdnet models
linked with django models.'''
    def __init__(self,djmodel,model):
        self.djmodel = djmodel
        self._setmodel(model)
        self.dj      = djmodel.objects
        
    #def get(self, **kwargs):
    #    try:
    #       return self._get(**kwargs)
    #    except self.model.DoesNotExist:
    #        pass
    #    try:
    #        dobj = self.djmodel.objects.get(**kwargs)
    #    except ObjectDoesNotExist:
    #        raise self.model.DoesNotExist
    #    return self.update_from_django(dobj)
        
    def update_from_django(self, dobj, instance = None):
        if instance is None:
            instance = self.model(id = dobj.id)
        for field in instance._meta.scalarfields:
            name = field.name
            if name is not LINKED_OBJECT_ATTRIBUTE:
                val = getattr(dobj,name,None)
                if val is not None:
                    setattr(instance,name,val)
        setattr(instance,LINKED_OBJECT_ATTRIBUTE,dobj)
        instance.save()
        logger.debug('Updated linked stdmodel %s' % instance)
        return instance
        
    def synch(self):
        '''Methdo used to synchrnonise linked models'''
        djall = self.dj.all()
        ids = set()
        for obj in djall:
            obj.save()
            ids.add(obj.id)
        for obj in self.all():
            if obj.id not in ids:
                obj.delete()
