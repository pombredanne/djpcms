from djpcms import sites, ispy3k

if ispy3k:
    from ._py3 import *
else:
    from ._py2 import *
    

def serve(port = 0, host = '127.0.0.1', use_reloader = False):
    server = CherryPyWSGIServer((host,port),sites.wsgi)
    server.start()
