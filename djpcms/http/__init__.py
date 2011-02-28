
def get_http(lib):
    '''Fetch the HTTP library.'''
    if lib == 'django':
        from djpcms.http import _django as mod
    elif lib == 'werkzeug':
        from djpcms.http import _werkzeug as mod
    else:
        raise NotImplementedError
    return mod


def serve(using = None, **kwargs):
    '''Serve DJPCMS applications'''
    if not using:
        from djpcms import sites
        using = sites.settings.HTTP_LIBRARY
    mod = get_http(using)
    mod.serve(**kwargs)
    
    