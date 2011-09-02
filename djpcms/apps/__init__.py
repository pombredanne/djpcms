from .site import *
from .permissions import *
from .innerblocks import *


class SiteLoader(object):
    _loaded = False
    
    def __call__(self):
        if not self._loaded:
            self._loaded = True
            self.load()
        return sites

    def load(self):
        raise NotImplemenetedError