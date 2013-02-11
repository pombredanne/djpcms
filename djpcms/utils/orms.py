from inspect import isclass
from collections import Mapping

from pulsar.utils import jsontools

from .httpurl import itervalues, iteritems, to_string
from .structures import OrderedDict
from .importer import import_module
from .text import nicename, UnicodeMixin, slugify

model_wrappers = OrderedDict()
model_from_hash = {}

ORMS = lambda : model_wrappers.values()


def orm_instance(instance):
    return getattr(instance, 'underlying_model_instance', instance)


class ModelType(type):
    pass


class Model(ModelType('ModelBase', (UnicodeMixin,), {})):
    id = None

    @classmethod
    def query(cls):
        return cls

    @classmethod
    def filter(cls, **kwargs):
        raise NotImplementedError()

    @classmethod
    def exclude(cls, **kwargs):
        raise NotImplementedError()


class DoesNotExist(Exception):
    pass


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
    orm = 'djpcms'
    DoesNotExist = DoesNotExist
    FieldValueError = DoesNotExist
    model = None

    def __init__(self, model):
        self.model = model
        self.test()
        self.setup()
        if self.hash:
            model_from_hash[self.hash] = model

    def __unicode__(self):
        return self.model.__name__

    @property
    def hash(self):
        return 'djpcms-%s' % id(self.model)

    @property
    def htmlclass(self):
        return slugify(self.__unicode__()).lower()

    def setup(self):
        pass

    def test(self):
        '''Test if this is the right mapper for :attr:`model`. If not it
must raise a ValueError. This method needs to be implemented by subclasses.'''
        if not isinstance(self.model, ModelType):
            raise ValueError()

    def instance(self, instance):
        raise NotImplementedError
    
    # Metadata methods
    def field_for_query(self, name):
        '''Check if the field *name* is available in the underlying model.'''
        return name
    
    # Query methods

    def query(self):
        '''Return a query class for the model.
This method needs to be implemented by subclasses.'''
        return self.model
    
    def filter_query(self, query, **filters):
        return query

    def filter(self, **kwargs):
        '''Return a query class for the model.
This method needs to be implemented by subclasses.'''
        return self.model.filter(**kwargs)

    def exclude(self, **kwargs):
        '''Return a query class for the model.
This method needs to be implemented by subclasses.'''
        return self.model.exclude(**kwargs)

    def get(self, **kwargs):
        '''Return a single instance of the model base on some
filtering (usually id). Similar to :meth:`fileter` method.'''
        return self.model.get(**kwargs)

    def query_from_mapping(self, mapping):
        '''Build a query from a *mapping*.

:paramater mapping: a mapping inluding :class:`MultiValueDict`.
:rtype: a dictionary of parameters to be passed to the :meth:`query` method'''
        r = {}
        if hasattr(mapping, 'lists'):
            mapping = mapping.lists()
        elif isinstance(mapping, Mapping):
            mapping = iteritems(mapping)
        for field, v in mapping:
            field = self.field_for_query(field)
            if field:
                if isinstance(v, (list, tuple)) and len(v) == 1:
                    v = v[0]
                r[field] = v
        return r

    def is_query(self, query):
        return True

    def __call__(self, *args, **kwargs):
        return self.model(*args, **kwargs)

    def _hash(self):
        raise NotImplementedError()

    def pretty_repr(self, instance):
        '''Return a string with a pretty representation of instance'''
        return to_string(instance)

    def model_attribute(self, name):
        pass

    def query_instance(self, qs, instance = None):
        return qs

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

    def save(self, data, instance=None, commit=True):
        raise NotImplementedError()

    def save_as_new(self, instance, data=None, commit=True):
        '''Save the existing *instance* as a new instance in the backend
 database.

 :parameter instance: an instance of :attr:`model`
 :parameter data: optional dictionary of fields to override
 :parameter commit: if to commit to backend
 :rtype: a new instance of :attr:`model`.
 '''
        raise NotImplementedError()

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
        '''Setup the environment for the ORM  library. Called during
 site initialisation.'''
        pass

    @classmethod
    def flush_models(cls, models=None):
        pass


def RegisterORM(orm):
    '''Register a new Object Relational Mapper to djpcms.'''
    global model_wrappers
    model_wrappers[orm.orm] = orm

def flush_models(models=None):
    global model_wrappers
    for wrapper in model_wrappers.values():
        wrapper.flush_models(models)

RegisterORM(OrmWrapper)

def register_wrapper(wrapper):
    setattr(wrapper.model, '_djpcms_orm_wrapper', wrapper)

def getmodel(appmodel):
    global _models
    for wrapper in _models.itervalues():
        try:
            return wrapper(appmodel)
        except:
            continue
    raise ValueError('Model {0} not recognised'.format(appmodel))
def mapper(model):
    '''Return an instance of a ORM djpcms wrapper'''
    if model is None:
        return
    elif isinstance(model, OrmWrapper):
        return model
    elif not isinstance(model, type):
        instance = orm_instance(model)
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
            yield id, str(mp)


class JSONEncoder(jsontools.JSONDateDecimalEncoder):
    """
    Provide custom serializers for JSON-RPC.
    """
    def default(self, obj):
        try:
            super(JSONEncoder, self).default(obj)
        except ValueError:
            mp = mapper(obj)
            if mp:
                return mp.hash
            else:
                raise ValueError("%s is not JSON serialisable" % obj)


json_hook = jsontools.date_decimal_hook