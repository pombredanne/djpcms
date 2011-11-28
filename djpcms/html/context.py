
__all__ = ['ContextRenderer']

class ContextRenderer(object):
    
    def __init__(self, djp, context = None, template = None, renderer = None,
                 text = None):
        self.djp = djp
        self.template = template
        self.context = context or {}
        self.renderer = renderer
        self._renderers = []
        if text is not None:
            self.text = text
        
    @classmethod
    def make(cls, txt):
        if isinstance(txt,cls):
            return txt
        else:
            return ContextRenderer(None,text = txt)
        
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
            return self.djp.render_template(self.template,self.context)
        elif self.renderer:
            return self.renderer(self.djp,self.context)
        else:
            raise NotImplementedError
        
    def add_renderer(self, r):
        if hasattr(r,'__call__'):
            if self.called:
                self.text = r(self.text)
            else:
                self._renderers.append(r)

