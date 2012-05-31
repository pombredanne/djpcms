from inspect import isclass
from datetime import date, datetime

import djpcms
from djpcms.utils.httpurl import itervalues
from djpcms.html import nicerepr
from djpcms.core.exceptions import ModelException
from djpcms.utils.structures import OrderedDict
from djpcms.utils.importer import import_module
from djpcms.utils.text import nicename, UnicodeMixin, to_string

model_wrappers = OrderedDict()
model_from_hash = {}

ORMS = lambda : model_wrappers.values()


class OrmWrapper(UnicodeMixin):
    '''Wrapper for object relational mapper libraries.

:parameter model: The ORM model class (for example a django model class).


.. attribute:: orm

    object relational mapper name
    
.. attribute:: model

    The model class.
    
.. attribute:: DoesNotExist

    proxy to the exception thrown when a query for a model instance produce
    no results.
    
.. attribute:: FieldValueError

    proxy to the exception thrown when a model field has wrong value.

'''
    orm = None
    hash = None
    DoesNotExist = None
    FieldValueError = None
    model = None
    short_description = 'short_description'
    module_name = None
    
    def __init__(self, model):
        self.orig_model = model
        self.model = model
        self.appmodel = None
        self.nicename = None
        self.test()
        self.setup()
        if self.hash:
            model_from_hash[self.hash] = model
        
    def __unicode__(self):
        return str(self.model)
    
    def setup(self):
        pass
    
    def test(self):
        '''Test if this is the right mapper for :attr:`model`. If not it
must raise a ValueError.
'''
        raise NotImplementedError
    
    def query(self):
        '''Return a query class for the model'''
        raise NotImplementedError
    
    def filter(self, **kwargs):
        '''Return a query class for the model'''
        raise NotImplementedError
    
    def get(self, **kwargs):
        '''Return a query class for the model'''
        raise NotImplementedError
        
    def is_query(self, query):
        return True
    
    def __call__(self, *args, **kwargs):
        return self.model(*args, **kwargs)
                
    @classmethod
    def clear(cls):
        pass
    
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
        return nicerepr(self._getrepr(name,instance),nd)
    
    def _getrepr(self, name, instance):
        attr = getattr(instance,name,None)
        if hasattr(attr,'__call__'):
            attr = attr()
        if attr is not None:
            return force_str(attr, strings_only = True)
        else:
            return sites.settings.DJPCMS_EMPTY_VALUE
        
    def id(self, obj):
        return obj.id
    
    def unique_id(self, obj = None):
        '''A unique id for Html purposes. Here we remove dots
since they seems to confuse jQuery selectors.'''
        id = obj
        if hasattr(obj,'id'):
            id = obj.id
        uuid = self.hash
        if id:
            uuid = '{0}-{1}'.format(uuid,id)
        return 'o-{0}'.format(uuid.replace('.','_'))
    
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


def RegisterORM(name):
    '''Register a new Object Relational Mapper to Djpcms. ``name`` is the
dotted path to a python module containing a class named ``OrmWrapper``
derived from :class:`BaseOrmWrapper`.'''
    global model_wrappers
    if isclass(name):
        if not name.orm:
            raise ValueError('"orm" not defined in OrmWrapper')
        model_wrappers[name.orm] = name
        if name.model:
            register_wrapper(name(name.model))
    else:
        names = name.split('.')
        if len(names) == 1:
            mod_name = 'djpcms.core.orms._' + name
        else:
            mod_name = name
        try:
            mod = import_module(mod_name)
        except ImportError as e:
            return
        model_wrappers[name] = mod.OrmWrapper


def register_wrapper(wrapper):
    setattr(wrapper.model,'_djpcms_orm_wrapper',wrapper)
    
    
def getmodel(appmodel):
    global _models
    for wrapper in _models.itervalues():
        try:
            return wrapper(appmodel)
        except:
            continue
    raise ModelException('Model {0} not recognised'.format(appmodel))

def mapper(model):
    '''Return an instance of a ORM djpcms wrapper'''
    if model is None:
        return
    elif isinstance(model,OrmWrapper):
        return model
    elif not isinstance(model, type):
        instance = model
        model = instance.__class__
    wrapper = getattr(model,'_djpcms_orm_wrapper',None)    
    if not wrapper:
        for wrapper_cls in ORMS():
            try:
                wrapper = wrapper_cls(model)
                break
            except ValueError:
                continue
        if not wrapper:
            return None
            return DummyMapper(model)
        else:
            register_wrapper(wrapper)
    return wrapper


def getid(obj):
    '''If ``obj`` is an instance of a ORM it returns its id'''
    if obj:
        try:
            return obj.id
        except (AttributeError, SyntaxError):
            return obj
    else:
        return obj
        

def registered_models_tuple():
    for model in model_from_hash.values():
        mp = mapper(model)
        id = mp.hash
        if id:
            yield id,mp.nicename
            