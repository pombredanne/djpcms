import hashlib

from py2py3 import iteritems, to_string

import django

from djpcms import sites
from djpcms.utils import force_str
from djpcms.template import loader

from .base import _boolean_icon, nicerepr, BaseOrmWrapper


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
        
    def _hash(self):
        sha = hashlib.sha1('django({0})'.format(self.meta))
        return sha.hexdigest()
        
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

    def _getrepr(self, name, instance):
        from django.db import models
        from django.contrib.admin.util import display_for_field, lookup_field
        try:
            f, attr, value = lookup_field(name, instance, self.model_admin)
        except (AttributeError, self.DoesNotExist):
            result_repr = self.get_value(instance, name, sites.settings.DJPCMS_EMPTY_VALUE)
        else:
            if f is None:
                allow_tags = getattr(attr, 'allow_tags', False)
                boolean = getattr(attr, 'boolean', False)
                if boolean:
                    allow_tags = True
                    result_repr = _boolean_icon(value)
                else:
                    result_repr = force_str(value)
                # Strip HTML tags in the resulting text, except if the
                # function has an "allow_tags" attribute set to True.
            else:
                if value is None:
                    result_repr = sites.settings.DJPCMS_EMPTY_VALUE
                if isinstance(f.rel, models.ManyToOneRel):
                    result_repr = getattr(instance, f.name)
                else:
                    result_repr = display_for_field(value, f)
        return result_repr

    @classmethod
    def clear(cls):
        from django.db.models.loading import cache
        d = cache.__dict__
        d['app_store'].clear()
        d['app_models'].clear()
        d['app_errors'].clear()
        d['loaded'] = False
        d['handled'].clear()
        d['postponed'] = []
        d['nesting_level'] = 0
        d['_get_models_cache'].clear()
    
    def save(self, data, instance = None, commit = True):
        if not instance:
            instance = self.model(**data)
        else:
            for name,value in iteritems(data):
                setattr(instance,name,value)
        if commit:
            instance.save()
        return instance
            
