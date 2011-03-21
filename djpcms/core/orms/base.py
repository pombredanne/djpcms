from datetime import date, datetime

from djpcms import sites, nodata
from djpcms.html import icons, nicerepr
from djpcms.utils import force_str
from djpcms.utils.text import nicename
from djpcms.template import loader

__all__ = ['BaseOrmWrapper',
           'nicerepr']


class BaseOrmWrapper(object):
    '''Base class for classes used to
wrap existing object relational mappers.

:parameter model: The ORM model class (for example a django model class).


.. attribute:: model

    The model class.

'''
    orm = None
    '''Object Relational Mapper name'''
    DoesNotExist = None
    '''Exception raise when an object is not available'''
    
    def __init__(self, model):
        self.model = model
        self.appmodel = None
        self.test()
        self.setup()
        self.hash = self._hash()
        sites.model_from_hash[self.hash] = model
        
    def setup(self):
        pass
    
    def test(self):
        raise NotImplementedError
    
    @classmethod
    def clear(cls):
        pass
    
    def __repr__(self):
        return str(self.model)
    __str__ = __repr__
    
    def _hash(self):
        raise NotImplementedError
    
    def pretty_repr(self, instance):
        '''Return a string with a pretty representation of instance'''
        return force_str(instance)
    
    def set_application(self, appmodel):
        self.appmodel = appmodel
        self.list_display = appmodel.list_display or []
        self.object_display = appmodel.object_display or self.list_display
        self.list_display_links = appmodel.list_display_links or []
        self.search_fields = appmodel.search_fields or []
        
    def getrepr(self, name, instance):
        attr = getattr(instance,name,None)
        if hasattr(attr,'__call__'):
            return attr()
        else:
            return attr
        
    def model_to_dict(self, instance, fields = None, exclude = None):
        raise NotImplementedError
    
    def _label_for_field(self, name):
        return nicename(name)
        
    def appfuncname(self, name):
        return 'objectfunction__%s' % name
    
    def get_value(self, instance, name, default = nodata):
        default = default if default is not nodata else sites.settings.DJPCMS_EMPTY_VALUE
        func = getattr(self.appmodel,self.appfuncname(name),None)
        if func:
            return func(instance)
        else:
            return default
    
    def label_for_field(self, name):
        '''Get the lable for field or attribute or function *name*.'''
        try:
            return self._label_for_field(name)
        except:
            pass
        try:
            if self.appmodel:
                func = getattr(self.appmodel,self.appfuncname(name),None)
                if func:
                    return func(name)
                else:
                    return self.appmodel.get_label_for_field(name)
        except:
            return name
        
    def getrepr(self, name, instance, nd = 3):
        '''representation of field *name* for *instance*.'''
        return nicerepr(self._getrepr(name,instance),nd)
    
    def _getrepr(self, name, instance):
        attr = getattr(instance,name,None)
        if hasattr(attr,'__call__'):
            attr = attr()
        if attr is not None:
            return force_str(attr, strings_only = True)
        else:
            return sites.settings.DJPCMS_EMPTY_VALUE
        
    def has_add_permission(self, user, obj=None):
        return user.is_superuser
    
    def has_change_permission(self, user, obj=None):
        return user.is_superuser
    
    def has_view_permission(self, user, obj = None):
        return True
    
    def has_delete_permission(self, user, obj=None):
        return user.is_superuser
    
    def get_object_id(self, obj):
        return '%s-%s' % (self.module_name,obj.id)
    
    def unique_id(self, obj):
        '''Create a unique ID for the object'''
        return '%s-%s' % (self.module_name,obj.id)
    
    def save(self, data, instance = None, commit = True):
        raise NotImplementedError

    @classmethod
    def setup_environment(cls,sites_):
        pass
