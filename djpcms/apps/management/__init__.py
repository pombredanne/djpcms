#
# MANAGEMENT COMMANDS LOGIC
#
import os
import sys
import argparse

import djpcms
from djpcms.utils.importer import import_module

from .base import Command, CommandError, CommandOption
                                        
__all__ = ['Command','CommandError','CommandOption',
           'call_command','execute']


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


def call_command(name, *args, **options):
    """
    Calls the given command, with the given options and args/kwargs.

    This is the primary API you should use for calling specific commands.

    Some examples:
        call_command('syncdb')
        call_command('shell', plain=True)
        call_command('sqlall', 'myapp')
    """
    # Load the command object.
    try:
        app_name = get_commands()[name]
        if isinstance(app_name, BaseCommand):
            # If the command is already loaded, use it directly.
            klass = app_name
        else:
            klass = load_command_class(app_name, name)
    except KeyError:
        raise CommandError("Unknown command: %r" % name)

    # Grab out a list of defaults from the options. optparse does this for us
    # when the script runs from the command line, but since call_command can
    # be called programatically, we need to simulate the loading and handling
    # of defaults (see #10080 for details).
    defaults = dict([(o.dest, o.default)
                     for o in klass.option_list
                     if o.default is not NO_DEFAULT])
    defaults.update(options)

    return klass.execute(*args, **defaults)


class ManagementUtility(object):
    """
    Encapsulates the logic of the django-admin.py and manage.py utilities.

    A ManagementUtility has a number of commands, which can be manipulated
    by editing the self.commands dictionary.
    """
    def __init__(self, sites, argv=None):
        if argv is None:
            argv = sys.argv[:]
        self.prog_name = os.path.basename(argv[0])
        self.argv = argv[1:]
        if hasattr(sites,'__call__'):
            self.callable = sites
            self.sites = sites()
        else:
            self.sites = sites
            self.sites.load()
            self.callable = lambda : self.sites

    def get_parser(self):
        return argparse.ArgumentParser(usage = self.get_usage())
        
    def get_usage(self):
        """
        Returns the script's main help text, as a string.
        """
        settings = self.sites.settings
        commands = self.sites.get_commands()
        usage = "\nType '{0} help <subcommand>' for help on a specific\
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
        if not command:
            parser = self.get_parser()
            parser.parse_args(argv)
            sys.exit(1)
        elif command == 'django':
            from django.core.management import ManagementUtility
            argv = [sys.prog_name] + argv[1:]
            utility = ManagementUtility(argv)
            utility.execute()
        else:
            self.fetch_command(command).run_from_argv(self.callable,
                                                      command,
                                                      argv[1:])


def execute(sites, argv=None, **params):
    '''Execute a command against a sites instance'''
    utility = ManagementUtility(sites,argv,**params)
    utility.execute()
    return utility.sites
