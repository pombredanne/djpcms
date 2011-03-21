import djpcms
from djpcms.utils import lazyattr, force_str

__all__ = ['LazyRender',
           'LazyUnicode']
        
        
class LazyUnicode(djpcms.UnicodeMixin):
    
    def __len__(self):
        return len(self.__unicode__())
    
    @lazyattr
    def __unicode__(self):
        return self.render()
    
    def render(self):
        raise NotImplementedError
    
    
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

    