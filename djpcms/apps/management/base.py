"""\
Command management. Originally from django. Modified and reduced.
"""

import os
import sys
import argparse

import djpcms
from djpcms.core.exceptions import ImproperlyConfigured, CommandError
        
        
class CommandOption(object):
    
    def __init__(self, name = None, cli = None, type = None, nargs = None,
                 action = None, description = None, default = None):
        self.name = name
        self.cli = cli
        self.type = type
        self.nargs = nargs
        self.action = action
        self.description = description
        self.default = default
    
    def add_argument(self, parser):
        kwargs = {}
        if self.type and self.type != 'string':
            kwargs["type"] = self.type
            
        if self.cli:
            args = tuple(self.cli)
            kwargs.update({
                        "dest": self.name,
                       "action": self.action or "store",
                       "default": self.default,
                       "help": "%s [%s]" % (self.description, self.default)})
            if kwargs["action"] != "store":
                kwargs.pop("type",None)
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

    def get_version(self):
        """Return the djpcms version, which should be correct for all
built-in djpcms commands. User-supplied commands should override this method.
        """
        return djpcms.get_version()

    def create_parser(self, command):
        """
        Create and return the ``OptionParser`` which will be used to
        parse the arguments to this command.
        """
        parser = argparse.ArgumentParser(description = self.help or command)
        parser.add_argument('--version',
                            action = 'version',
                            version = self.get_version(),
                            help = "Show the command's version number and exit")
        for opt in self.option_list:
            opt.add_argument(parser)
        return parser

    def print_help(self, prog_name, subcommand):
        """
        Print the help message for this command, derived from
        ``self.usage()``.

        """
        parser = self.create_parser(prog_name, subcommand)
        parser.print_help()

    def run_from_argv(self, sites, command, argv):
        parser = self.create_parser(command)
        options = parser.parse_args(argv)
        self.execute(sites, options)

    def execute(self, sites, options):
        """Try to execute this command. If the command raises a
        ``CommandError``, intercept it and print it sensibly to
        stderr.
        """
        try:
            self.stdout = sys.stdout
            self.stderr = sys.stderr
            output = self.handle(sites, options)
            if output:
                self.stdout.write(output)
        except CommandError as e:
            self.stderr.write(smart_str(self.style.ERROR('Error: %s\n' % e)))
            sys.exit(1)

    def handle(self, options):
        """The actual logic of the command. Subclasses must implement
        this method.
        """
        raise NotImplementedError()
