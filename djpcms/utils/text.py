from gzip import GzipFile

from py2py3 import ispy3k
if ispy3k:
    from io import BytesIO
else:
    from StringIO import StringIO as BytesIO

from .strings import force_str

def capfirst(x):
    x = force_str(x).strip()
    if x:
        return x[0].upper() + x[1:]
    else:
        return x

nicename = lambda name : force_str(capfirst(name.replace('-',' ').replace('_',' ')))



# From http://www.xhaus.com/alan/python/httpcomp.html#gzip
# Used with permission.
def compress_string(s):
    zbuf = BytesIO()
    zfile = GzipFile(mode='wb', compresslevel=6, fileobj=zbuf)
    zfile.write(s)
    zfile.close()
    return zbuf.getvalue()