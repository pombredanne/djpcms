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
                                        
__all__ = ['Command', 'CommandError', 'CommandOption',
           'fetch_command', 'execute']


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


def fetch_command(sites, name, argv=None, **params):
    """Fetch a command name"""
    utility = ManagementUtility(sites, argv, **params)
    return utility.fetch_command(name)
    

def execute(sites, argv=None, **params):
    '''Execute a command against a sites instance'''
    utility = ManagementUtility(sites, argv, **params)
    return utility.execute()



class ManagementUtility(object):
    """
    Encapsulates the logic of the django-admin.py and manage.py utilities.

    A ManagementUtility has a number of commands, which can be manipulated
    by editing the self.commands dictionary.
    """
    def __init__(self, site_factory, argv = None):
        if argv is None:
            argv = sys.argv[:]
        self.prog_name = os.path.basename(argv[0])
        self.argv = argv[1:]
        self.site_factory = site_factory
        self.sites = site_factory()

    def get_parser(self):
        return argparse.ArgumentParser(usage = self.get_usage())
        
    def get_usage(self):
        """
        Returns the script's main help text, as a string.
        """
        settings = self.sites.settings
        commands = self.sites.get_commands()
        usage = "\nType '{0} <subcommand> --help' for help on a specific\
 subcommand.\n\nAvailable subcommands:\n".format(self.prog_name)
        cmds = '\n'.join(('  %s' % cmd for cmd in sorted(commands)))
        text = '{0}\n{1}'.format(usage,cmds)
        if settings.DESCRIPTION:
            text = '{0}\n{1}'.format(settings.DESCRIPTION,text)
        if settings.EPILOG:
            text = '{0}\n{1}'.format(text,settings.EPILOG)
        return text

    def fetch_command(self, subcommand):
        """Tries to fetch the given *subcommand*, printing a message with the
appropriate command called from the command line (usually
        "django-admin.py" or "manage.py") if it can't be found.
        """
        try:
            app_name = self.sites.get_commands()[subcommand]
        except KeyError:
            sys.stderr.write("Unknown command: %r\nType '%s help'\
 for usage.\n" % (subcommand, self.prog_name))
            sys.exit(1)
        if isinstance(app_name, Command):
            # If the command is already loaded, use it directly.
            klass = app_name
        else:
            klass = load_command_class(app_name, subcommand)
        return klass

    def execute(self):
        """Given the command-line arguments, this figures out which
subcommand is being run, creates a parser appropriate to that command,
and runs it."""
        argv = self.argv
        command = argv[0] if argv else 'help'
        
        # Allow for django commands, for example
        # python manage.py django syncdb
        if command == 'help':
            parser = self.get_parser()
            parser.parse_args(argv)
            sys.exit(1)
        elif command == 'django':
            from django.core.management import ManagementUtility
            argv = [sys.prog_name] + argv[1:]
            utility = ManagementUtility(argv)
            utility.execute()
        else:
            cmd = self.fetch_command(command)
            if self.site_factory.can_pickle:
                site_factory = pickle.loads(pickle.dumps(self.site_factory))
            else:
                site_factory = self.site_factory
            return cmd.run_from_argv(site_factory, command, argv[1:])

