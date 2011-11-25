'''Routing classes for managing urls.
'''
import re
import copy

from djpcms import UnicodeMixin, to_string
from djpcms.core.exceptions import ApplicationUrlException
from djpcms.utils import iri_to_uri, openedurl, SLASH
from djpcms.utils.strings import force_str


__all__ = ['Route','RouteMixin']


PATH_REGEX = '.*'

_rule_re = re.compile(r'''
    (?P<static>[^<]*)                           # static rule data
    <
    (?:
        (?P<converter>[a-zA-Z_][a-zA-Z0-9_]*)   # converter name
        (?:\((?P<args>.*?)\))?                  # converter arguments
        \:                                      # variable delimiter
    )?
    (?P<variable>[a-zA-Z_][a-zA-Z0-9_]*)        # variable name
    >
''', re.VERBOSE)
_simple_rule_re = re.compile(r'<([^>]+)>')
_converter_args_re = re.compile(r'''
    ((?P<name>\w+)\s*=\s*)?
    (?P<value>
        True|False|
        \d+.\d+|
        \d+.|
        \d+|
        \w+|
        [urUR]?(?P<stringval>"[^"]*?"|'[^']*')
    )\s*,
''', re.VERBOSE|re.UNICODE)


_PYTHON_CONSTANTS = {
    'None':     None,
    'True':     True,
    'False':    False
}


def _pythonize(value):
    if value in _PYTHON_CONSTANTS:
        return _PYTHON_CONSTANTS[value]
    for convert in int, float:
        try:
            return convert(value)
        except ValueError:
            pass
    if value[:1] == value[-1:] and value[0] in '"\'':
        value = value[1:-1]
    return unicode(value)


def parse_converter_args(argstr):
    argstr += ','
    args = []
    kwargs = {}

    for item in _converter_args_re.finditer(argstr):
        value = item.group('stringval')
        if value is None:
            value = item.group('value')
        value = _pythonize(value)
        if not item.group('name'):
            args.append(value)
        else:
            name = item.group('name')
            kwargs[name] = value

    return tuple(args), kwargs


def parse_rule(rule):
    """Parse a rule and return it as generator. Each iteration yields tuples
    in the form ``(converter, arguments, variable)``. If the converter is
    `None` it's a static url part, otherwise it's a dynamic one.

    :internal:
    """
    pos = 0
    end = len(rule)
    do_match = _rule_re.match
    used_names = set()
    while pos < end:
        m = do_match(rule, pos)
        if m is None:
            break
        data = m.groupdict()
        if data['static']:
            yield None, None, data['static']
        variable = data['variable']
        converter = data['converter'] or 'default'
        if variable in used_names:
            raise ValueError('variable name %r used twice.' % variable)
        used_names.add(variable)
        yield converter, data['args'] or None, variable
        pos = m.end()
    if pos < end:
        remaining = rule[pos:]
        if '>' in remaining or '<' in remaining:
            raise ValueError('malformed url rule: %r' % rule)
        yield None, None, remaining


class RouteMixin(object):

    def route(self):
        raise NotImplementedError
    
    @property
    def path(self):
        return self.route().path


class Route(UnicodeMixin):
    '''Routing in djpcms with ides from werkzeug.
    
.. attribute: url

    a route template string
    
'''
    def __init__(self, url = '', append_slash = False):
        self.__url = openedurl(str(url or ''))
        self.path = ''
        self.targs = 0
        self.nargs = 0
        self.breadcrumbs = []
        self.names = []
        if self.__url:
            self.__process()
            self.path = SLASH + self.path
    
    def __len__(self):
        return len(self.__url)
    
    def __eq__(self, other):
        if isinstance(other,self.__class__):
            return to_string(self) == to_string(other)
        else:
            return False
        
    def __lt__(self, other):
        if isinstance(other,self.__class__):
            return to_string(self) < to_string(other)
        else:
            raise TypeError('Cannot compare {0} with {1}'.format(self,other))
        
    def __unicode__(self):
        if self.append_slash:
            return to_string('^{0}$'.format(self.__url))
        else:
            return to_string('^{0}'.format(self.__url))

    def get_url(self, **kwargs):
        if kwargs:
            return iri_to_uri(self.path % kwargs)
        else:
            if self.names:
                raise ApplicationUrlException('Missing key-value\
 arguments for {0} regex'.format(self.path))
            return self.path
    
    def __process(self):
        names = []
        front = self.__url
        back = ''
        star = '*'
        while front:
            st = front.find('(') + 1
            en = front.find(')')
            if st and en:
                st -= 1
                en += 1
                names.append(front[st:en])
                back += front[:st] + star
                front = front[en:]
            else:
                back += front
                front = None
        
        bits = back.split(SLASH)
        for bit in bits:
            if not bit:
                continue
            if bit == star:
                bit = names.pop(0)
                st = bit.find('<') + 1
                en = bit.find('>')
                if st and en:
                    name = bit[st:en]
                else:
                    raise ApplicationUrlException('Regular expression for urls\
 requires a keyworld. %s does not have one.' % bit) 
                bit  = '%(' + name + ')s'
                self.names.append(name)
            self.breadcrumbs.append(bit)
        self.path = SLASH.join(self.breadcrumbs)

    def _get_url(self):
        return self.__url
    
    def __add__(self, other):
        if not self.append_slash:
            raise ValueError('Cannot prepend to another url.\
 Append slash is set to false')
        cls = self.__class__
        append_slash = True
        if isinstance(other,cls):
            append_slash = other.append_slash
            other = other._get_url()
        else:
            other = str(other)
        return self.__class__(self.__url + other,
                              append_slash = append_slash)
        
        
ALL_REGEX = '.*'
PATH_RE = '(?P<path>{0})'.format(ALL_REGEX)
IDREGEX = '(?P<id>\d+)'
SLUG_REGEX = '[-\.\+\#\'\:\w]+'
UUID_REGEX = '(?P<id>[-\w]+)'
ALL_URLS = Route(PATH_RE)

RegExUrl = Route 