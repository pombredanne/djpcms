import re
import logging
import json
import unicodedata
from uuid import uuid4

from py2py3 import ispy3k

from .strings import *
from .jsontools import *
from .numbers import *
from .urls import *

if ispy3k:
    import pickle
else:
    import cPickle as pickle


def gen_unique_id():
    return str(uuid4())


def merge_dict(d1,d2):
    d = d1.copy()
    d.update(d2)
    return d

    
def lazyattr(f):
    '''Decorator which can be used on a member function.
It stores the result for futures uses.
    '''
    name = '_lazy_%s' % f.__name__
    
    def _(self, *args, **kwargs):
        if not hasattr(self,name):
            v = f(self, *args, **kwargs)
            setattr(self,name,v)
        return getattr(self,name)
        
    _.__doc__ = f.__doc__
    
    return _


def storegenarator(f):
    '''Decorator which can be used on a member function
returning a generator. It stores the generated results for future use.
    '''
    name = '_generated_%s' % f.__name__
    def _(self, *args, **kwargs):
        if not hasattr(self,name):
            items = []
            setattr(self,name,items)
            append = items.append
            for g in f(self, *args, **kwargs):
                append(g)
                yield g
        else:
            for g in getattr(self,name):
                yield g
                
    _.__doc__ = f.__doc__
    
    return _
        

class lazyjoin(object):
    
    def __init__(self, sep):
        self.sep = sep
        
    def __call__(self, f):
        
        def _(obj, *args, **kwargs):
            return self.sep.join(f(*args,**kwargs))
        
        return _
        

def setlazyattr(obj,name,value):
    name = '_lazy_%s' % name
    setattr(obj,name,value)
    
    
@lazyjoin('/')
def safepath(path, rtx = '-'):
    for p in path.split('/'):
        if p:
            yield slugify(p, rtx = rtx)

    
def slugify(value, rtx = '-'):
    '''Normalizes string, removes non-alpha characters,
and converts spaces to hyphens *rtx* character'''
    value = unicodedata.normalize('NFKD', force_str(value)).encode('ascii', 'ignore')
    value = force_str(re.sub('[^\w\s-]', '', value.decode()).strip())
    return re.sub('[-\s]+', rtx, value)


def logtrace(logger, request, exc_info, status = 500):
    '''Log a stack trace'''
    if status == 404:
        msg = 'URL not found: %s' % request.path
        log = logger.warn
    else:
        status = status or 500
        msg = 'Internal Server Error at url "%s"' % request.path
        log = logger.error
    log(msg, exc_info=exc_info, extra={
                                       'status_code': status,
                                       'request':request
                                       })
