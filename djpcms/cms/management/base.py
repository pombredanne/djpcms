"""\
Command management. Originally from django. Modified and reduced.
"""
import os
import sys
import argparse
import logging
from copy import copy

import djpcms
from djpcms.cms.exceptions import CommandError
from djpcms.utils.log import dictConfig


class CommandOption(object):

    def __init__(self, name=None, cli=None, type=None, nargs=None,
                 action=None, description=None, default=None,
                 metavar=None):
        self.name = name
        self.cli = cli
        self.type = type
        self.nargs = nargs
        self.action = action
        self.description = description
        self.default = default
        self.metavar = metavar

    def add_argument(self, parser):
        kwargs = {}
        if self.type and self.type != 'string':
            kwargs["type"] = self.type
        if self.metavar:
            kwargs["metavar"] = self.metavar
        if self.cli:
            args = tuple(self.cli)
            kwargs.update({
                       "dest": self.name,
                       "action": self.action or "store",
                       "default": self.default,
                       "help": "%s [%s]" % (self.description, self.default)})
            if kwargs["action"] != "store":
                kwargs.pop("type",None)
            if self.nargs:
                kwargs['nargs'] = self.nargs
        elif self.nargs and self.name:
            args = (self.name,)
            description = "%s [%s]" % (self.description, self.default) if\
                     self.default else self.description
            kwargs.update({'nargs':self.nargs,
                           'help': description,
                           'default': self.default})
        else:
            return

        parser.add_argument(*args, **kwargs)


class Command(object):
    """The base class from which all management commands ultimately derive.

Use this class if you want access to all of the mechanisms which
parse the command-line arguments and work out what code to call in
response.

.. attribute: help

    The text to display when requesting help for the command.
"""
    help = ''
    option_list = ()

    def __init__(self, name):
        self.name = name

    def clone(self, website, argv, stdout=None, stderr=None):
        me = copy(self)
        me._website = website
        me.argv = argv
        me.stdout = stdout
        me.stderr = stderr
        me.logger = logging.getLogger('Command.%s' % me.name)
        return me

    def get_version(self):
        """Return the djpcms version, which should be correct for all
built-in djpcms commands. User-supplied commands should override this method.
        """
        return djpcms.__version__

    def get_options(self):
        '''Parse the command arguments and return options.'''
        parser = argparse.ArgumentParser(description=self.help or self.name)
        parser.add_argument('--version',
                            action='version',
                            version=self.get_version(),
                            help="Show the command's version number and exit")
        for opt in self.option_list:
            opt.add_argument(parser)
        return parser.parse_args(self.argv)

    def __call__(self, **kwargs):
        '''Execute this command'''
        options = self.get_options()
        sys_stdout = sys.stdout
        sys_stderr = sys.stderr
        sys.stdout = self.stdout or sys_stdout
        sys.stderr = self.stderr or sys_stderr
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        try:
            return self.handle(options, **kwargs)
        except CommandError as e:
            self.logger.critical('Command error', exc_info=True)
        finally:
            sys.stdout = sys_stdout
            sys.stderr = sys_stderr

    def handle(self, site_factory, options):
        """The actual logic of the command. Subclasses must implement
        this method.
        """
        raise NotImplementedError()

    def website(self, options):
        site = self._website.site()
        self.setup_logging(site.settings, options)
        return site

    def setup_logging(self, settings, options):
        '''Setup logging for :class:`Command`. Override if you need to.'''
        LOGGING = {
              'version': 1,
              'disable_existing_loggers': False,
              'formatters': {
                    'simple': {'format': '%(message)s'},
                    },
            'handlers': {
                    'simple': {
                        'level': 'DEBUG',
                        'class': 'logging.StreamHandler',
                        'formatter': 'simple'
                    },
            },
            'root': {
                    'handlers': ['simple'],
                    'level': 'DEBUG',
            }
        }
        dictConfig(LOGGING)
