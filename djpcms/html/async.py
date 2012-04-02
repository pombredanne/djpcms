from djpcms.utils import is_string
from djpcms.utils.py2py3 import iteritems


__all__ = ['Renderer',
           'DeferredRenderer',
           'DeferredDataRenderer',
           'ContextRenderer',
           'StreamRenderer']


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
    
    
class DeferredRenderer(Renderer):
    
    def __init__(self):
        self._called = False
        self._result = None
        
    @property
    def called(self):
        return self._called
    
    @property
    def result(self):
        return self._result
        
    def render(self, *args, **kwargs):
        '''render ``self`` as html'''
        if self.called:
            return self._result
        else:
            return self._render(*args,**kwargs)
        
    def _render(self, *args, **kwargs):
        pass
        
    
class DeferredDataRenderer(DeferredRenderer):
    
    def __init__(self, stream):
        super(DeferredDataRenderer,self).__init__()
        self._renderers = []
        self.stream = data = guess_stream(stream)
        self.deferred = deferred = []
        setitem = self.setitem
        for key, value in iterdata(stream):
            if isinstance(value, Renderer):
                value = value.done()
                if isinstance(value, Renderer):
                    deferred.append((key, value))
            setitem(key, value)
    
    def add_renderer(self, r):
        '''Add new renderer to the list of renderer.'''
        if hasattr(r,'__call__'):
            if self.called:
                self._result = r(self._result)
            else:
                self._renderers.append(r)
        
    def _render(self):
        if self.deferred:
            deferred = []
            for key, value in self.deferred:
                new_value = value.done()
                if new_value != value:
                    self.setitem(key, new_value)
                else:
                    deferred.append((key, value))
            self.deferred = deferred
        if self.deferred:
            return self
        else:
            self._called = True
            stream = self.stream
            self.stream = None
            renderers = self._renderers
            self._renderers = []
            result = self.get_result(stream)
            for r in renderers:
                result = r(result)
            self._result = result
            return result

    def setitem(self, key, value):
        self.stream[key] = value
        
    def get_result(self, stream):
        return stream
        

class ContextRenderer(DeferredDataRenderer):
    
    def __init__(self, request, context, renderer):
        super(ContextRenderer,self).__init__(context)
        self.add_renderer(lambda r: renderer(request, r))
    
    
class StreamRenderer(DeferredDataRenderer):
    '''The stream is either a text of a ContextRenderer'''    
    def setitem(self, key, value):
        if value is None:
            value = ''
        elif not is_string(value) and not isinstance(value, Renderer):
            value = str(value)
        if key < len(self.stream):
            self.stream[key] = value
        else:
            self.stream.append(value)
            
    def get_result(self, data):
        return ''.join(data)