"""
Management utility to create superusers.
"""
import getpass
import re
import sys
from optparse import make_option

import djpcms

from sessions.models import User

try:
    input = raw_input
except NameError:
    pass


RE_VALID_USERNAME = re.compile('[\w.@+-]+$')


def get_default_username():
    # Try to determine the current system user's username to use as a default.
    try:
        default_username = getpass.getuser().replace(' ', '').lower()
    except (ImportError, KeyError):
        # KeyError will be raised by os.getpwuid() (called by getuser())
        # if there is no corresponding entry in the /etc/passwd file
        # (a very restricted chroot environment, for example).
        default_username = ''

    # Determine whether the default username is taken, so we don't display
    # it as an option.
    if default_username:
        try:
            User.objects.get(username=default_username)
        except User.DoesNotExist:
            pass
        else:
            default_username = ''
    
    return default_username


class Command(djpcms.Command):
    help = 'Used to create a superuser.'

    def handle(self, *args, **options):
        verbosity = int(options.get('verbosity', 1))
        username = None
        password = None
        default_username = get_default_username()
        
        try:

            # Get a username
            while 1:
                if not username:
                    input_msg = 'Username'
                    if default_username:
                        input_msg += ' (Leave blank to use %r)' % default_username
                    username = input(input_msg + ': ')
                if default_username and username == '':
                    username = default_username
                if not RE_VALID_USERNAME.match(username):
                    sys.stderr.write("Error: That username is invalid. Use only letters, digits and underscores.\n")
                    username = None
                    continue
                try:
                    User.objects.get(username=username)
                except User.DoesNotExist:
                    break
                else:
                    sys.stderr.write("Error: That username is already taken.\n")
                    username = None

            # Get a password
            while 1:
                if not password:
                    password = getpass.getpass()
                    password2 = getpass.getpass('Password (again): ')
                    if password != password2:
                        sys.stderr.write("Error: Your passwords didn't match.\n")
                        password = None
                        continue
                if password.strip() == '':
                    sys.stderr.write("Error: Blank passwords aren't allowed.\n")
                    password = None
                    continue
                break
        except KeyboardInterrupt:
            sys.stderr.write("\nOperation cancelled.\n")
            sys.exit(1)

        User.objects.create_superuser(username, password=password)
        if verbosity >= 1:
          self.stdout.write("Superuser created successfully.\n")

