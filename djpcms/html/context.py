from djpcms.utils import is_string

__all__ = ['ContextRenderer','StreamContextRenderer']
    
    
class ContextRenderer(object):
    '''Utility class for data that needs to be rendered in lazy
fashion. Once the data has rendered an instance of this class
has :attr:`called` evaluating to ``True``.

.. attribute:: called

    The instance has the rendered :attr:`text` available.

.. attribute:: text

    string representing the final result once available.
'''
    def __init__(self, request, context = None, template = None,
                 renderer = None, text = None):
        self.request = request
        self.template = template
        self.context = context if context is not None else {}
        self.renderer = renderer
        self._renderers = []
        if text is not None:
            self.text = text
        
    def __repr__(self):
        if self.called:
            return self.text
        else:
            return repr(self.context)
    __str__ = __repr__
    
    @classmethod
    def make(cls, txt):
        if isinstance(txt,cls):
            return txt
        else:
            return ContextRenderer(None, text = txt)
        
    @property
    def called(self):
        return hasattr(self,'text')
    
    def done(self):
        '''Return the text if already rendered otherwise return self'''
        if self.called:
            return self.text
        return self
    
    def render(self):
        if not self.called:
            self.text = text = self._render()
            renderers = self._renderers
            self._renderers = []
            for r in renderers:
                text = r(text)
            self.text = text
        return self.text
        
    def _render(self):
        if self.template:
            template = self.request.view.template
            return template.render(self.template,self.context)
        elif self.renderer:
            return self.renderer(self.request,**self.context)
        else:
            raise NotImplementedError
        
    def add_renderer(self, r):
        '''Add new renderer to the list of renderer.'''
        if hasattr(r,'__call__'):
            if self.called:
                self.text = r(self.text)
            else:
                self._renderers.append(r)


class StreamContextRenderer(ContextRenderer):
    '''The stream is either a text of a ContextRenderer'''
    def __init__(self, request, stream):
        data = []
        done = True
        for p,s in enumerate(stream):
            if isinstance(s,ContextRenderer):
                s = s.done()
                if isinstance(s,ContextRenderer):
                    done = False
            if not is_string(s) and not isinstance(s, ContextRenderer):
                s = str(s)
            data.append(s)
        text = '\n'.join(data) if done else None
        super(StreamContextRenderer,self).__init__(request, data, text = text)
    
    def _render(self):
        return '\n'.join(self.context)
        