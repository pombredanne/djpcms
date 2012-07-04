'''A micro-asyncronous script derived from twisted.'''
import os

if os.environ.get('DJPCMS_ASYNCHRONOUS_FRAMEWORK') == 'twisted':
    from twisted.internet.defer import *
    from twisted.python.failure import Failure
    
    def is_async(obj):
        return isinstance(obj, Deferred)
    
    def is_failure(obj):
        return isinstance(obj, Failure)
    
    def MultiDeferred(DeferredList):
        
        def __init__(self, stream, type=None):
            if not type:
                type = stream.__class__
            if self.type not in ('list',):
                raise TypeError('Multideferred type container must be a list')
            DeferredList.__init__(self, stream)
            
else:
    from pulsar.async.defer import *
    
    
def async_object(obj):
    '''Obtain the result if available, otherwise it returns self.'''
    if is_async(obj):
        return obj.result if obj.called and not obj.paused else obj
    else:
        return obj