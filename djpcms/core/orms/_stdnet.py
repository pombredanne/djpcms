import stdnet
from stdnet.orm import register_applications, StdNetType, model_to_dict

from py2py3 import iteritems

from djpcms.utils.text import nicename

from .base import BaseOrmWrapper


class OrmWrapper(BaseOrmWrapper):
    '''Djpcms ORM wrapper for stdnet

    https://github.com/lsbardel/python-stdnet'''
    orm = 'stdnet'
    
    def setup(self):
        self.meta = meta = self.model._meta
        self.objects     = self.model.objects
        self.module_name = meta.name
        self.app_label   = meta.app_label
        self.hash = meta.hash
        self.nicename = '{0} - {1}'.format(nicename(meta.app_label),
                                      nicename(meta.name))
        self.model_to_dict = model_to_dict
        self.DoesNotExist = self.model.DoesNotExist
        
    def __getattr__(self, name):
        return getattr(self.objects,name)
        
    def test(self):
        if not isinstance(self.model,StdNetType):
            raise ValueError
    
    def delete_all(self):
        self.model.flush()
        
    def save(self, data, instance = None, commit = True):
        if not instance:
            instance = self.model(**data)
        else:
            for name,value in iteritems(data):
                setattr(instance,name,value)
        if commit:
            return instance.save()
        else:
            return instance
    
    @classmethod
    def setup_environment(cls, sites):
        settings = sites.settings
        default = settings.DATASTORE.get('default',None)
        register_applications(settings.INSTALLED_APPS,
                              app_defaults = settings.DATASTORE,
                              default = default)
    


