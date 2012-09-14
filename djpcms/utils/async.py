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
    
    def maybe_async(obj):
        '''Obtain the result if available, otherwise it returns self.'''
        if is_async(obj):
            return obj.result if obj.called and not obj.paused else obj
        else:
            return obj
            
else:
    from pulsar.async.defer import *
    
def on_result(result, callback, *args, **kwargs):
    result = maybe_async(result)
    if is_async(result):
        return result.add_callback(lambda result:\
                    callback(result, *args, **kwargs))
    else:
        return callback(result, *args, **kwargs)
    
def log_and_execute(failure, errback, *args, **kwargs):
    log_failure(failure)
    return errback(failure, *args, **kwargs)
    

def log_on_error(result, errback, *args, **kwargs):
    if is_async(result):
        return result.add_errback(lambda failure:\
                    log_and_execute(failure, errback, *args, **kwargs))
    else:
        return result
    