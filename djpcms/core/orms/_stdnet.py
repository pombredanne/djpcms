from stdnet.orm import StdNetType, model_to_dict

from djpcms.utils.py2py3 import iteritems

from .base import BaseOrmWrapper


class OrmWrapper(BaseOrmWrapper):
    '''Djpcms ORM wrapper for stdnet
    
    https://github.com/lsbardel/python-stdnet'''
    def setup(self):
        self.meta = meta = self.model._meta
        self.objects     = self.model.objects
        self.module_name = meta.name
        self.app_label   = meta.app_label
        self.hash = meta.hash
        #
        self.model_to_dict = model_to_dict
        self.get = self.objects.get
        self.all = self.objects.all
        self.filter = self.objects.filter
        
    def test(self):
        if not isinstance(self.model,StdNetType):
            raise ValueError
            
    def _hash(self):
        return self.meta.hash
    
    def get_view_permission(self):
        return '%s_view' % self.meta.basekey()
    
    def get_add_permission(self):
        return '%s_add' % self.meta.basekey()
    
    def get_change_permission(self):
        return '%s_change' % self.meta.basekey()
    
    def get_delete_permission(self):
        return '%s_delete' % self.meta.basekey()
        
    def save(self, data, instance = None, commit = True):
        if not instance:
            instance = self.model(**data)
        else:
            for name,value in iteritems(data):
                setattr(instance,name,value)
        return instance.save(commit = commit)
    