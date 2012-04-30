#
# MANAGEMENT COMMANDS LOGIC
#
import os
import sys
import pickle
import argparse

import djpcms
from djpcms.utils.importer import import_module

from .base import Command, CommandError, CommandOption
                                        
__all__ = ['Command', 'CommandError', 'CommandOption', 'execute',
           'fetch_command']

def find_commands(management_dir):
    """
    Given a path to a management directory, returns a list of all the command
    names that are available.

    Returns an empty list if no commands are defined.
    """
    command_dir = os.path.join(management_dir, 'commands')
    try:
        return (f[:-3] for f in os.listdir(command_dir)
                if not f.startswith('_') and f.endswith('.py'))
    except OSError:
        return ()

def load_command_class(app_name, name):
    """
    Given a command name and an application name, returns the Command
    class instance. All errors raised by the import process
    (ImportError, AttributeError) are allowed to propagate.
    """
    module = import_module('%s.management.commands.%s' % (app_name, name))
    return module.Command()

def execute(website, argv=None, stdout=None, stderr=None):
    '''Execute a command against a sites instance'''
    utility = ManagementUtility(website, argv)
    return utility.execute(stdout=stdout, stderr=stderr)

def fetch_command(website, command, argv=None, stdout=None, stderr=None):
    utility = ManagementUtility(website, argv)
    cmd = utility.fetch_command(command)
    return lambda: cmd.run_from_argv(website, command, argv,
                                     stdout=stdout, stderr=stderr)
    


class ManagementUtility(object):
    """
    Encapsulates the logic of the django-admin.py and manage.py utilities.

    A ManagementUtility has a number of commands, which can be manipulated
    by editing the self.commands dictionary.
    """
    def __init__(self, website, argv = None):
        if argv is None:
            argv = sys.argv[:]
        self.prog_name = os.path.basename(argv[0])
        self.argv = argv[1:]
        self.website = website

    def get_parser(self, with_commands=True, nargs='?', **params):
        '''Get the argument parser'''
        if with_commands:
            params['usage'] = self.get_usage()
        p = argparse.ArgumentParser(**params)
        p.add_argument('command', nargs=nargs, help='command to run')
        p.add_argument('-c','--config',
                       default=self.website.settings_file,
                       help='The path to the config file.')
        p.add_argument('-v','--version',
                       action='version',
                       version=self.website.version or djpcms.__version__,
                       help='Print the version.')
        return p
        
    def get_usage(self):
        """
        Returns the script's main help text, as a string.
        """
        site = self.website()
        commands = site.get_commands()
        usage = "\nType '{0} <command> --help' for help on a specific\
 command.\n\nAvailable commands:\n".format(self.prog_name)
        cmds = '\n'.join(('  %s' % cmd for cmd in sorted(commands)))
        text = '{0}\n{1}'.format(usage,cmds)
        if site.settings.DESCRIPTION:
            text = '{0}\n{1}'.format(site.settings.DESCRIPTION, text)
        if site.settings.EPILOG:
            text = '{0}\n{1}'.format(text, site.settings.EPILOG)
        return '\n'+text

    def fetch_command(self, subcommand):
        """Tries to fetch the given *subcommand*, printing a message with the
appropriate command called from the command line (usually
        "django-admin.py" or "manage.py") if it can't be found.
        """
        site = self.website()
        try:
            app_name = site.get_commands()[subcommand]
        except KeyError:
            raise ValueError("Unknown command: %r\nType '%s help'\
 for usage.\n" % (subcommand, self.prog_name))
        if isinstance(app_name, Command):
            # If the command is already loaded, use it directly.
            klass = app_name
        else:
            klass = load_command_class(app_name, subcommand)
        return klass

    def execute(self, stdout=None, stderr=None):
        """Given the command-line arguments, this figures out which
subcommand is being run, creates a parser appropriate to that command,
and runs it."""
        argv = self.argv
        parser = self.get_parser(with_commands=False, add_help=False)
        args, _ = parser.parse_known_args(argv)
        self.website.settings_file = args.config
        parser = self.get_parser(add_help=False)
        args, argv = parser.parse_known_args(argv)
        if args.command:
            # Command is available. delegate the arg parsing to it
            cmd = self.fetch_command(args.command)
            website = pickle.loads(pickle.dumps(self.website))
            return cmd.run_from_argv(website, args.command, argv,
                                     stdout=stdout, stderr=stderr)
        else:
            # this should fail unless we pass -h
            parser = self.get_parser(nargs=1)
            parser.parse_args()
        

