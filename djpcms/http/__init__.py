from .utils import *

def get_http(lib=None):
    '''Fetch the HTTP library.'''
    if lib == 'django':
        from djpcms.http import _django as mod
    else:
        from djpcms.http import simple as mod
    return mod


def serve(using = None, **kwargs):
    '''Serve DJPCMS applications'''
    mod = get_http(using)
    mod.serve(**kwargs)
