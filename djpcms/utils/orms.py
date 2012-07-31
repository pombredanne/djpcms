from inspect import isclass

from .httpurl import itervalues, to_string
from .structures import OrderedDict
from .importer import import_module
from .text import nicename, UnicodeMixin, slugify

model_wrappers = OrderedDict()
model_from_hash = {}

ORMS = lambda : model_wrappers.values()


class ModelType(type):
    pass


class Model(ModelType('ModelBase', (object,), {})):
    id = None

    @classmethod
    def query(cls):
        return cls

    @classmethod
    def filter(cls, **kwargs):
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
    short_description = 'short_description'

    def __init__(self, model):
        self.model = model
        self.appmodel = None
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

    def query(self):
        '''Return a query class for the model.
This method needs to be implemented by subclasses.'''
        return self.model

    def filter(self, **kwargs):
        '''Return a query class for the model.
This method needs to be implemented by subclasses.'''
        return self.model.filter(**kwargs)

    def get(self, **kwargs):
        '''Return a single instance of the model base on some
filtering (usually id). Similar to :meth:`fileter` method.'''
        return self.model.get(**kwargs)

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

    def set_application(self, appmodel):
        self.appmodel = appmodel
        self.list_display = appmodel.list_display or []
        self.object_display = appmodel.object_display or self.list_display
        self.list_display_links = appmodel.list_display_links or []
        self.search_fields = appmodel.search_fields or []

    def label_for_field(self, field):
        if hasattr(field,'name'):
            return field.name
        elif hasattr(self.model,field):
            fun = getattr(self.model,field)
            if hasattr(fun,self.short_description):
                return fun.short_description
        return nicename(field)

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
        '''Setup the environment for thei ORM  library. Called during
 site initialization.'''
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
            yield id, str(mp)
