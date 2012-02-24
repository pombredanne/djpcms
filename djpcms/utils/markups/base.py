import os

_default_markup = None
MARKUP_HANDLERS = {}


__all__ = ['Application', 'add', 'choices', 'default', 'get']


class Application(object):
    code = None
    name = None
            
    def setup_extension(self, extension):
        pass
    
    def __call__(self, request, text):
        raise NotImplementedError()


def add(handler):
    '''Add new markup handler'''
    global _default_markup, MARKUP_HANDLERS
    code = handler.code
    if not _default_markup:
        _default_markup = code
    if not code in MARKUP_HANDLERS: 
        MARKUP_HANDLERS[code] = handler


def choices(*args,**kwargs):
    global MARKUP_HANDLERS
    yield ('','raw')
    for k in MARKUP_HANDLERS:
        yield k, MARKUP_HANDLERS[k].name


def default(*args,**kwargs):
    global _default_markup
    return _default_markup


def get(name):
    global MARKUP_HANDLERS
    return MARKUP_HANDLERS.get(name)
        

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
