'''\
Markup handlers for converting text into html. There are three
handlers implemented:

* creole
* Markdown (requires markdown2 package)
* restructuredText (requires sphinx package)

To use it::

    from djpcms.utils import markups
    
    html = markups.get('rst')(txt)
'''
import os
from djpcms.utils.importer import import_module

from .base import *

_loaded = False
def load():
    '''Load markup applications.'''
    global _loaded
    if not _loaded:
        path = os.path.split(os.path.abspath(__file__))[0]
        for name in os.listdir(path):
            if not (name.startswith('_') or name.endswith('.pyc')):
                name = name.split('.')[0]
                if name == 'base':
                    continue
                try:
                    appmod = import_module('djpcms.utils.markups.'+name)
                except:
                    pass
                else:
                    add(appmod.Application())
        _loaded = True
        

load()