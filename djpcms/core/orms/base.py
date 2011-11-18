from datetime import date, datetime
from inspect import isclass

from djpcms import UnicodeMixin
from djpcms.utils import force_str
from djpcms.utils.text import nicename


__all__ = ['OrmWrapper',
           'OrmQuery',
           'DummyMapper',
           'model_from_hash']


model_from_hash = {}


class OrmQuery(object):
    '''Wrapper for an Model query'''
    def __init__(self, query, mapper):
        self.query = query
        self.mapper = mapper
    

class OrmWrapper(UnicodeMixin):
    '''Wrapper for object relational mapper libraries.

:parameter model: The ORM model class (for example a django model class).


.. attribute:: model

    The model class.

'''
    orm = None
    '''Object Relational Mapper name'''
    DoesNotExist = None
    '''Exception raise when an object is not available'''
    short_description = 'short_description'
    module_name = None
    
    def __init__(self, model):
        self.model = model
        self.appmodel = None
        self.hash = None
        self.nicename = None
        self.test()
        self.setup()
        if self.hash:
            model_from_hash[self.hash] = model
        
    def setup(self):
        pass
    
    def test(self):
        raise NotImplementedError
    
    def is_query(self, query):
        return True
    
    def __call__(self, query):
        if self.is_query(query):
            return query
        elif query is not None:
            return OrmQuery(query,self)
                
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
    
    def model_attribute(self, name):
        pass
    
    def query_instance(self, qs, instance = None):
        return qs     
    
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
        #TODO
        #REMOVE FROM HERE
        from djpcms.html import nicerepr
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
    
    def class_name(self, obj = None):
        obj = obj or self.model
        name = obj.__name__ if isclass(obj) else obj.__class__.__name__
        return name.lower()
    
    def save(self, data, instance = None, commit = True):
        raise NotImplementedError
    
    def save_as_new(self, instance, data = None, commit = True):
        '''Save the existing *instance* as a new instance in the backend
 database.
 
 :parameter instance: an instance of :attr:`model`
 :parameter data: optional dictionary of fields to override
 :parameter commit: if to commit to backend
 :rtype: a new instance of :attr:`model`. 
 '''
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
    def setup_environment(cls,sites):
        '''Setup the environment for thei ORM  library. Called during
 site initialization.'''
        pass


class DummyMapper(OrmWrapper):
    
    def test(self):
        pass
    
    def all(self):
        return self.model.all()
        