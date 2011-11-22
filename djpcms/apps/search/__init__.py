'''
The search application is designed to facilitate the integration of
a search engine into your web site. It is flexible enough to allow for any
custom engine.


Setup
~~~~~~~~~~~~~~

To use the application you need to 

    from djpcms.apps.included import search
    
    app = search.Application('/search/', engine = mysearchengine)
'''
from .search import *