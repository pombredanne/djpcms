import djpcms
from djpcms.utils import lazyattr


class LazyRender(djpcms.UnicodeMixin):
    
    def __init__(self, elem):
        self.elem = elem
        
    def __len__(self):
        return len(self.render())
    
    @lazyattr
    def render(self):
        return self.elem.render()
    
    def __unicode__(self):
        return self.render()