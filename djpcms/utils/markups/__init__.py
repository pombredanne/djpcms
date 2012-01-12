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

_loaded = False
_default_markup = None
MARKUP_HANDLERS = {}


class Application(object):
    code = None
    name = None
            
    def setup_extension(self, extension):
        pass
    
    def __call__(self, request, text):
        raise NotImplementedError()


def add(handler):
    '''
    Add new markup handler
    '''
    global _default_markup, MARKUP_HANDLERS
    code = handler.code
    if not _default_markup:
        _default_markup = code
    if not code in MARKUP_HANDLERS: 
        MARKUP_HANDLERS[code] = handler


def choices():
    load()
    global MARKUP_HANDLERS
    yield ('','raw')
    for k in MARKUP_HANDLERS:
        yield k, MARKUP_HANDLERS[k].name


def default():
    load()
    global _default_markup
    return _default_markup


def get(name):
    load()
    global MARKUP_HANDLERS
    return MARKUP_HANDLERS.get(name)


def load():
    '''Load markup applications.'''
    global _loaded
    if not _loaded:
        path = os.path.split(os.path.abspath(__file__))[0]
        for name in os.listdir(path):
            if not name.startswith('_'):
                name = name.split('.')[0] 
                try:
                    appmod = import_module('djpcms.utils.markups.'+name)
                except ImportError as e:
                    pass
                else:
                    add(appmod.Application())
        _loaded = True
        

def help(code = 'crl'):
    c = get(code)
    if not c:
        return ''
    else:
        d = os.path.split(os.path.abspath(__file__))[0]
        templ = os.path.join(d,'code','%s-help.txt' % c['name'])
        try:
            f = open(templ,'r')
        except:
            return ''
        data = f.read()
        return c['handler'](data)

