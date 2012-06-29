'''A micro-asyncronous script derived from twisted.'''
import os

if os.environ.get('DJPCMS_ASYNCHRONOUS_FRAMEWORK') == 'twisted':
    from twisted.internet.defer import *
    
    def is_async(obj):
        return isinstance(obj, Deferred)
    
    def MultiDeferred(DeferredList):
        
        def __init__(self, stream, type=None):
            if not type:
                type = stream.__class__
            if self.type not in ('list',):
                raise TypeError('Multideferred type container must be a list')
            DeferredList.__init__(self, stream)
            
else:
    from pulsar.async.defer import *