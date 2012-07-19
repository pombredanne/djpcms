import re
from unicodedata import normalize
from uuid import uuid4

from .httpurl import to_string, string_type, ispy3k

NOTHING = ('', None)

def gen_unique_id():
    return str(uuid4())

def capfirst(x):
    x = to_string(x).strip()
    if x:
        return x[0].upper() + x[1:]
    else:
        return x
    
def nicename(name):
    name = to_string(name)
    return capfirst(' '.join(name.replace('-',' ').replace('_',' ').split()))

def slugify(value, rtx = '-'):
    '''Normalizes string, removes non-alpha characters,
and converts spaces to hyphens *rtx* character'''
    value = normalize('NFKD', to_string(value)).encode('ascii', 'ignore')
    value = to_string(re.sub('[^\w\s-]', '', value.decode()).strip())
    return re.sub('[-\s]+', rtx, value)
    
def mark_safe(v):
    return SafeString(v)

def is_safe(v):
    return getattr(v, '__html__', False)

def escape(html, force=False):
    """Returns the given HTML with ampersands,
quotes and angle brackets encoded."""
    if hasattr(html,'__html__') and not force:
        return html
    if html in NOTHING:
        return ''
    else:
        return to_string(html).replace('&', '&amp;').replace('<', '&lt;')\
            .replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

def smart_escape(text):
    if is_safe(text):
        return text
    lines = to_string(text).split('\n')
    if len(lines) > 1:
        r = len(lines)
        return '<textarea rows="{0}" readonly="readonly">{1}</textarea>'.format(r,escape(text))
        #return '<p>{0}</p>'.format('</p><p>'.join((escape(text) for text in lines)))
    else:
        return escape(text)
    

class SafeString(string_type):
    __html__ = True
    
    
if ispy3k:
    
    class UnicodeMixin(object):
        
        def __unicode__(self):
            return '{0} object'.format(self.__class__.__name__)
        
        def __str__(self):
            return self.__unicode__()
        
        def __repr__(self):
            return '%s: %s' % (self.__class__.__name__,self)
        
else: # Python 2    # pragma nocover
    
    class UnicodeMixin(object):
        
        def __unicode__(self):
            return unicode('{0} object'.format(self.__class__.__name__))
        
        def __str__(self):
            return self.__unicode__().encode()
        
        def __repr__(self):
            return '%s: %s' % (self.__class__.__name__,self)