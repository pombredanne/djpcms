import hashlib

from py2py3 import iteritems, to_string

import django

from .base import BaseOrmWrapper


def django_hash(model):
    sha = hashlib.sha1('django({0})'.format(model._meta))
    return sha.hexdigest()[:8]


class OrmWrapper(BaseOrmWrapper):
    orm = 'django'
    
    def setup(self):
        from django.forms.models import model_to_dict
        from django.contrib.admin.util import label_for_field
        from django.contrib.admin import site
        model_admin = site._registry.get(self.model,None)
        self.model_admin = model_admin
        self.meta = meta = self.model._meta
        self.module_name = meta.module_name
        self.app_label   = meta.app_label
        self.hash = django_hash(self.model)
        #
        self.objects = self.model.objects
        self.get = self.objects.get
        self.all = self.objects.all
        self.filter = self.objects.filter
        self.DoesNotExist = self.model.DoesNotExist
        #
        #Calculate the Hash id of metaclass `meta`
        self.model_to_dict = model_to_dict
        self._label_for_field = lambda name: to_string(label_for_field(name, self.model, self.model_admin))
        
    def test(self):
        from django.db.models.base import ModelBase
        if not isinstance(self.model,ModelBase):
            raise ValueError
    
    def has_add_permission(self, user, obj=None):
        return has_permission(user, self.get_add_permission(), obj)
    
    def has_change_permission(self, user, obj=None):
        return has_permission(user, self.get_change_permission(), obj)
    
    def has_view_permission(self, user, obj = None):
        return has_permission(user, self.get_view_permission(), obj)
    
    def has_delete_permission(self, user, obj=None):
        return has_permission(user, self.get_delete_permission(), obj)
    
    def get_view_permission(self):
        return '%s_view' % self.meta
    
    def get_add_permission(self):
        opts = self.meta
        return opts.app_label + '.' + opts.get_add_permission()
    
    def get_change_permission(self):
        opts = self.meta
        return opts.app_label + '.' + opts.get_change_permission()
    
    def get_delete_permission(self):
        opts = self.meta
        return opts.app_label + '.' + opts.get_delete_permission()

    def save(self, data, instance = None, commit = True):
        if not instance:
            instance = self.model(**data)
        else:
            for name,value in iteritems(data):
                setattr(instance,name,value)
        if commit:
            instance.save()
        return instance
    
    @classmethod
    def setup_environment(cls, sites):
        sites.settings.setup_django(True)
           
