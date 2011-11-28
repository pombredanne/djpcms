'''Routing classes for managing urls.
Several classes were originally taken in november 2011
from the routing module in werkzeug_.
They have been consequently adapted for djpcms.

Original License

:copyright: (c) 2011 by the Werkzeug Team, see AUTHORS for more details.
:license: BSD

.. _werkzeug: https://github.com/mitsuhiko/werkzeug
'''
import re
import copy

from djpcms import UnicodeMixin, to_string, py2py3
from djpcms.utils import iri_to_uri, remove_double_slash, urlquote

from .exceptions import UrlException


__all__ = ['Route']


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
            raise ValueError('variable name {0} used twice in rule {1}.'\
                             .format(variable,rule))
        used_names.add(variable)
        yield converter, data['args'] or None, variable
        pos = m.end()
    if pos < end:
        remaining = rule[pos:]
        if '>' in remaining or '<' in remaining:
            raise ValueError('malformed url rule: %r' % rule)
        yield None, None, remaining


class Route(UnicodeMixin):
    '''Routing in djpcms with ideas from werkzeug.
    
:parameter rule: Rule strings basically are just normal URL paths
    with placeholders in the format ``<converter(arguments):name>``
    where the converter and the arguments are optional.
    If no converter is defined the `default` converter is used which
    means `string`.
'''
    def __init__(self, rule, defaults = None, append_slash = False):
        rule = remove_double_slash(str(rule))
        # all rules must start with a slash
        if rule.startswith('/'):
            rule = rule[1:]
        if rule and append_slash and not rule.endswith('/'):
            rule += '/'
        rule = '/' + rule
        self.defaults = defaults or {}
        self.is_leaf = not rule.endswith('/')
        self.rule = rule[1:]
        self.arguments = set(map(str, self.defaults))
        self.breadcrumbs = []
        self._converters = {}
        regex_parts = []
        for converter, arguments, variable in parse_rule(self.rule):
            if converter is None:
                regex_parts.append(re.escape(variable))
                if variable != '/':
                    self.breadcrumbs.append((False,variable))
            else:
                convobj = get_converter(converter, arguments)
                regex_parts.append('(?P<%s>%s)' % (variable, convobj.regex))
                self.breadcrumbs.append((True,variable))
                self._converters[variable] = convobj
                self.arguments.add(str(variable))
        self._regex_string = ''.join(regex_parts)
        self._regex = re.compile(self.regex, re.UNICODE)
    
    @property
    def regex(self):
        if self.is_leaf:
            return '^' + self._regex_string + '$'
        else:
            return '^' + self._regex_string
    
    def __hash__(self):
        return hash(self.rule)
    
    def __unicode__(self):
        return self.rule
    
    @property
    def path(self):
        return '/' + self.rule
    
    def __eq__(self, other):
        if isinstance(other,self.__class__):
            return str(self) == str(other)
        else:
            return False
        
    def __lt__(self, other):
        if isinstance(other,self.__class__):
            return to_string(self) < to_string(other)
        else:
            raise TypeError('Cannot compare {0} with {1}'.format(self,other))

    def _url_generator(self, values):
        for is_dynamic, val in self.breadcrumbs:
            if is_dynamic:
                val = self._converters[val].to_url(values[val])
            yield val
            
    def url(self, **values):
        if self.defaults:
            d = self.defaults.copy()
            values = d.update(values)
        url = '/' + '/'.join(self._url_generator(values))
        return url if self.is_leaf else url + '/'
    
    def match(self, path):
        match = self._regex.search(path)
        if match is not None:
            remaining = path[match.end():]
            groups = match.groupdict()
            result = {}
            for name, value in py2py3.iteritems(groups):
                try:
                    value = self._converters[name].to_python(value)
                except UrlException:
                    return
                result[str(name)] = value
            if remaining:
                result['__remaining__'] = remaining
            return result

    def __add__(self, other):
        if self.is_leaf:
            raise ValueError('Cannot prepend {0} to another route.\
 It is a leaf.'.format(self))
        cls = self.__class__
        rule = other.rule if isinstance(other,cls) else str(other)
        return cls(self.rule + rule)
        

class BaseConverter(object):
    """Base class for all converters."""
    regex = '[^/]+'
    weight = 100

    def to_python(self, value):
        return value

    def to_url(self, value):
        return urlquote(value)


class UnicodeConverter(BaseConverter):
    """This converter is the default converter and accepts any string but
    only one path segment.  Thus the string can not include a slash.

    This is the default validator.

    Example::

        Rule('/pages/<page>'),
        Rule('/<string(length=2):lang_code>')

    :param minlength: the minimum length of the string.  Must be greater
                      or equal 1.
    :param maxlength: the maximum length of the string.
    :param length: the exact length of the string.
    """

    def __init__(self, minlength=1, maxlength=None, length=None):
        if length is not None:
            length = '{%d}' % int(length)
        else:
            if maxlength is None:
                maxlength = ''
            else:
                maxlength = int(maxlength)
            length = '{%s,%s}' % (
                int(minlength),
                maxlength
            )
        self.regex = '[^/]' + length


class AnyConverter(BaseConverter):
    """Matches one of the items provided.  Items can either be Python
    identifiers or strings::

        Rule('/<any(about, help, imprint, class, "foo,bar"):page_name>')

    :param items: this function accepts the possible items as positional
                  arguments.
    """

    def __init__(self, *items):
        self.regex = '(?:%s)' % '|'.join([re.escape(x) for x in items])


class PathConverter(BaseConverter):
    """Like the default :class:`UnicodeConverter`, but it also matches
    slashes.  This is useful for wikis and similar applications::

        Rule('/<path:wikipage>')
        Rule('/<path:wikipage>/edit')
    """
    regex = '[^/].*?'
    weight = 200


class NumberConverter(BaseConverter):
    """Baseclass for `IntegerConverter` and `FloatConverter`.

    :internal:
    """
    weight = 50

    def __init__(self, fixed_digits=0, min=None, max=None):
        self.fixed_digits = fixed_digits
        self.min = min
        self.max = max

    def to_python(self, value):
        if (self.fixed_digits and len(value) != self.fixed_digits):
            raise UrlException()
        value = self.num_convert(value)
        if (self.min is not None and value < self.min) or \
           (self.max is not None and value > self.max):
            raise UrlException()
        return value

    def to_url(self, value):
        if (self.fixed_digits and len(str(value)) > self.fixed_digits):
            raise ValueError()
        value = self.num_convert(value)
        if (self.min is not None and value < self.min) or \
           (self.max is not None and value > self.max):
            raise ValueError()
        if self.fixed_digits: 
            value = ('%%0%sd' % self.fixed_digits) % value
        return str(value)


class IntegerConverter(NumberConverter):
    """This converter only accepts integer values::

        Rule('/page/<int:page>')

    This converter does not support negative values.

    :param fixed_digits: the number of fixed digits in the URL.  If you set
                         this to ``4`` for example, the application will
                         only match if the url looks like ``/0001/``.  The
                         default is variable length.
    :param min: the minimal value.
    :param max: the maximal value.
    """
    regex = r'\d+'
    num_convert = int


class FloatConverter(NumberConverter):
    """This converter only accepts floating point values::

        Rule('/probability/<float:probability>')

    This converter does not support negative values.

    :param min: the minimal value.
    :param max: the maximal value.
    """
    regex = r'\d+\.\d+'
    num_convert = float

    def __init__(self, min=None, max=None):
        super(FloatConverter,self).__init__(0, min, max)


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


def get_converter(name, arguments):
    c = _CONVERTERS.get(name)
    if not c:
        raise LookupError('Route converter {0} not available'.format(name))
    if arguments:
        args, kwargs = parse_converter_args(arguments)
        return c(*args,**kwargs)
    else:
        return c()

    
#: the default converter mapping for the map.
_CONVERTERS = {
    'default':          UnicodeConverter,
    'string':           UnicodeConverter,
    'any':              AnyConverter,
    'path':             PathConverter,
    'int':              IntegerConverter,
    'float':            FloatConverter
}
