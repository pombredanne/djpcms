'''
The search application is designed to facilitate the integration of
a search engine into your web site. It is flexible enough to allow for any
custom engine.


Setup
~~~~~~~~~~~~~~

To use the application you need to add it to your application urls along these
lines:: 

    from djpcms.apps import search
    
    urls = (...,
            search.Application('/search/', engine = mysearchengine),
            ...
            )
    
The ``mysearchengine`` is the actual search engine perfoming queries and text
searching.
'''
from .forms import search_form
from .search import *