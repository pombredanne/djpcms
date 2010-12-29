# -*- coding: utf-8 -*-
"""
ORIGINAL

flask.config
~~~~~~~~~~~~

Implements the configuration related objects.

:copyright: (c) 2010 by Armin Ronacher.
:license: BSD, see LICENSE for more details.

ADAPTED for use in djpcms
"""
from copy import copy

class NoValue:
    pass


class Config(dict):
    """Works exactly like a dict but provides ways to fill it from files
or special dictionaries. There are two common patterns to populate the
config.

Either you can fill the config from a config file::

app.config.from_pyfile('yourconfig.cfg')

Or alternatively you can define the configuration options in the
module that calls :meth:`from_object` or provide an import path to
a module that should be loaded. It is also possible to tell it to
use the same module and with that provide the configuration values
just before the call::

DEBUG = True
SECRET_KEY = 'development key'
app.config.from_object(__name__)

In both cases (loading from any Python file or loading from modules),
only uppercase keys are added to the config. This makes it possible to use
lowercase values in the config file for temporary values that are not added
to the config or to define the config keys in the same file that implements
the application.

Probably the most interesting way to load configurations is from an
environment variable pointing to a file::

app.config.from_envvar('YOURAPPLICATION_SETTINGS')

In this case before launching the application you have to set this
environment variable to the file you want to use. On Linux and OS X
use the export statement::

export YOURAPPLICATION_SETTINGS='/path/to/config/file'

On windows use `set` instead.

:param root_path: path to which files are read relative from. When the
config object is created by the application, this is
the application's :attr:`~flask.Flask.root_path`.
:param defaults: an optional dictionary of default values
"""

    def __init__(self, root_path = None, parent = None, defaults=None):
        dict.__init__(self, defaults or {})
        self.parent = parent
        self.root_path = root_path

    def from_envvar(self, variable_name, silent=False):
        """Loads a configuration from an environment variable pointing to
a configuration file. This basically is just a shortcut with nicer
error messages for this line of code::

app.config.from_pyfile(os.environ['YOURAPPLICATION_SETTINGS'])

:param variable_name: name of the environment variable
:param silent: set to `True` if you want silent failing for missing
files.
:return: bool. `True` if able to load config, `False` otherwise.
"""
        rv = os.environ.get(variable_name)
        if not rv:
            if silent:
                return False
            raise RuntimeError('The environment variable %r is not set '
                               'and as such configuration could not be '
                               'loaded. Set this variable and make it '
                               'point to a configuration file' %
                               variable_name)
        self.from_pyfile(rv)
        return True

    def from_pyfile(self, filename):
        """Updates the values in the config from a Python file. This function
behaves as if the file was imported as module with the
:meth:`from_object` function.

:param filename: the filename of the config. This can either be an
absolute filename or a filename relative to the
root path.
"""
        if not self.root_path:
            raise ValueError('No root path available. Cannot load from pyfile')
        filename = os.path.join(self.root_path, filename)
        d = imp.new_module('config')
        d.__file__ = filename
        try:
            execfile(filename, d.__dict__)
        except IOError, e:
            e.strerror = 'Unable to load configuration file (%s)' % e.strerror
            raise
        self.from_object(d)

    def from_object(self, obj):
        """Updates the values from the given object. An object can be of one
of the following two types:

- a string: in this case the object with that name will be imported
- an actual object reference: that object is used directly

Objects are usually either modules or classes.

Just the uppercase variables in that object are stored in the config
after lowercasing. Example usage::

app.config.from_object('yourapplication.default_config')
from yourapplication import default_config
app.config.from_object(default_config)

You should not use this function to load the actual configuration but
rather configuration defaults. The actual config should be loaded
with :meth:`from_pyfile` and ideally from a location not within the
package because the package might be installed system wide.

:param obj: an import name or object
"""
        if isinstance(obj, basestring):
            obj = import_string(obj)
        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, dict.__repr__(self))
    
    def __getattr__(self, key):
        v = self.get(key,NoValue)
        if v is NoValue:
            if self.parent:
                return getattr(self.parent,key)
            else:
                raise AttributeError('No attribute {0} avaialble'.format(key))
        else:
            return v
        
    def copy(self):
        obj = self.__class__()
        obj.root_path = self.root_path
        for k,v in self.items():
            if isinstance(v,Config):
                v = v.copy()
                v.parent = obj
            obj[k] = v
        return obj
