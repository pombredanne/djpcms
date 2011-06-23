from datetime import date, datetime

from djpcms import sites, nodata, UnicodeMixin
from djpcms.html import icons, nicerepr
from djpcms.utils import force_str
from djpcms.utils.text import nicename
from djpcms.template import loader

__all__ = ['BaseOrmWrapper',
           'DummyMapper',
           'nicerepr']


class BaseOrmWrapper(UnicodeMixin):
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
    short_description = 'short_description'
    
    def __init__(self, model):
        self.model = model
        self.appmodel = None
        self.test()
        self.setup()
        sites.model_from_hash[self.hash] = model
        
    def setup(self):
        pass
    
    def test(self):
        raise NotImplementedError
    
    @classmethod
    def clear(cls):
        pass
    
    def __unicode__(self):
        return str(self.model)
    
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
        
    def model_to_dict(self, instance, fields = None, exclude = None):
        raise NotImplementedError
    
    def label_for_field(self, field):
        if hasattr(field,'name'):
            return field.name
        elif hasattr(self.model,field):
            fun = getattr(self.model,field)
            if hasattr(fun,self.short_description):
                return fun.short_description
        return nicename(field)
    
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
    
    def unique_id(self, obj = None):
        '''A unique id for Html purposes. Here we remove dots
since they seems to confuse jQuery selectors.'''
        if obj:
            id = obj.uuid
        else:
            id = self.model.hash
        return 'o-{0}'.format(id.replace('.','-'))
    
    def save(self, data, instance = None, commit = True):
        raise NotImplementedError
    
    def search_text(self, qs, search_string, slist):
        '''\
Perform a full text search on the model.

:parameter qs: initial query where the search is applied.
:parameter search_string: a string to search.
:parameter slist: a list of fields to search.

Return an iterable over items'''
        raise NotImplementedError('Cannot perform text search. Not implemented')

    def delete_all(self):
        self.all().delete()
        
    @classmethod
    def setup_environment(cls,sites_):
        pass


class DummyMapper(BaseOrmWrapper):
    
    def __init__(self, model):
        self.model = model
    
    def all(self):
        return self.model.all()
        