from inspect import isclass

import djpcms
from djpcms.utils.py2py3 import itervalues
from djpcms.core.exceptions import ModelException
from djpcms.utils.structures import OrderedDict
from djpcms.utils.importer import import_module

from .base import *

model_wrappers = OrderedDict()

ORMS = lambda : model_wrappers.values()


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
    if not isinstance(model,type):
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
            