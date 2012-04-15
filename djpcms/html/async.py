import logging

from djpcms.utils.py2py3 import iteritems
from djpcms.utils.async import Deferred, MultiDeferred, Failure
from djpcms.utils import mark_safe

__all__ = ['Renderer',
           'DeferredDataRenderer',
           'ContextRenderer',
           'StreamRenderer']


LOGGER = logging.getLogger('djpcms')

def iterdata(stream):
    if isinstance(stream, dict):
        return iteritems(stream)
    else:
        return enumerate(stream)

def guess_stream(stream):
    if isinstance(stream, dict):
        return {}
    else:
        return []
    
    
class Renderer(object):
    '''A mixin for all classes which render into html.

.. attribute:: description

    An optional description of the renderer.
    
    Default ``""``
'''
    description = None
    
    def render(self, *args, **kwargs):
        '''render ``self`` as html'''
        raise NotImplementedError()
    
    def media(self, request):
        '''It returns an instance of :class:`Media`.
It should be overritten by derived classes.'''
        return None
    
    
class DeferredDataRenderer(Deferred):
    '''A :class:`Deferred` which renders to text.'''
    def __init__(self, stream):
        super(DeferredDataRenderer,self).__init__()
        typ = dict if isinstance(stream, dict) else list
        self.multi = multi = MultiDeferred(type=typ)
        multi.update(stream)
        multi.add_callback(self._finish)
        multi.lock()
    
    def _finish(self, result):
        result = self.result_from_stream(result)
        return self.callback(result)
        
    def _error(self, failure):
        LOGGER.critical('Unhandled error while rendering',
                        exc_info=failure.exc_info)
        return failure
    
    def result_from_stream(self, stream):
        return stream
        

class ContextRenderer(DeferredDataRenderer):
    
    def __init__(self, request, context, renderer):
        super(ContextRenderer, self).__init__(context)
        self.add_callback(lambda r: renderer(request, r))\
            .add_callback(mark_safe, self._error)
    
    
class FailureException(Exception):
    
    def __init__(self, failure):
        self.failure = failure
        
        
class StreamRenderer(DeferredDataRenderer):
    '''The stream is either a text of a ContextRenderer'''
    def __init__(self, stream):
        super(StreamRenderer, self).__init__(stream)
        self.add_callback(mark_safe, self._error)
            
    def _result_from_stream(self, stream):
        for value in stream:
            if value is None:
                continue
            elif isinstance(value, bytes):
                yield value.decode('utf-8')
            elif isinstance(value, str):
                yield value
            elif isinstance(value, Failure):
                raise FailureException(value)
            else:
                yield str(value)
            
    def result_from_stream(self, stream):
        try:
            return ''.join(self._result_from_stream(stream))
        except FailureException as f:
            return f.failure
    