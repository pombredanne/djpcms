import hashlib
import operator
from functools import reduce

from py2py3 import iteritems, to_string

import django

from .base import BaseOrmWrapper


def construct_search(field_name):
    # use different lookup methods depending on the notation
    if field_name.startswith('^'):
        return "%s__istartswith" % field_name[1:]
    elif field_name.startswith('='):
        return "%s__iexact" % field_name[1:]
    elif field_name.startswith('@'):
        return "%s__search" % field_name[1:]
    else:
        return "%s__icontains" % field_name


def isexact(bit):
    if not bit:
        return bit
    N = len(bit)
    Nn = N - 1
    bc = '%s%s' % (bit[0],bit[Nn])
    if bc == '""' or bc == "''":
        return bit[1:Nn]
    else:
        return bit
    

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
    
    def search_text(self, qs, search_string, slist):
        from django.db.models import Q
        from django.db.models.query import QuerySet
        bits  = search_string.split()
        for bit in bits:
            bit = isexact(bit)
            if not bit:
                continue
            or_queries = [Q(**{construct_search(field_name): bit}) \
                          for field_name in slist]
            other_qs   = QuerySet(self.model)
            other_qs.dup_select_related(qs)
            other_qs   = other_qs.filter(reduce(operator.or_, or_queries))
            qs         = qs & other_qs
        return qs
    
    @classmethod
    def setup_environment(cls, sites):
        sites.settings.setup_django(True)
           
