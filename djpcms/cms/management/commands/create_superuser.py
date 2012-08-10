"""Management utility to create superusers."""
import getpass
import re
import sys

from djpcms import cms

try:
    input = raw_input
except NameError:
    pass


RE_VALID_USERNAME = re.compile('[\w.@+-]+$')


def get_def_username(site):
    # Try to determine the current system user's username to use as a default.
    try:
        def_username = getpass.getuser().replace(' ', '').lower()
    except (ImportError, KeyError):
        # KeyError will be raised by os.getpwuid() (called by getuser())
        # if there is no corresponding entry in the /etc/passwd file
        # (a very restricted chroot environment, for example).
        def_username = ''
    # Determine whether the default username is taken, so we don't display
    # it as an option.
    if def_username:
        user = site.permissions.get_user(username=def_username)
        if user:
            def_username = ''
    return def_username


class Command(cms.Command):
    help = 'Used to create a superuser.'

    def handle(self, options):
        site = self.website(options)
        if not site.User:
            raise RuntimeError('User model not available')
        username = None
        password = None
        def_username = get_def_username(site)
        input_msg = 'Username'
        if def_username:
            input_msg += ' (Leave blank to use %s)' % def_username
        try:
            # Get a username
            while not username:
                username = input(input_msg + ': ')
                if def_username and username == '':
                    username = def_username
                if not RE_VALID_USERNAME.match(username):
                    sys.stderr.write('Error: That username is invalid. Use '
                                     'only letters, digits and underscores.\n')
                    username = None
                elif site.permissions.get_user(username=username):
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
        user = site.permissions.create_superuser(username=username,
                                                 password=password)
        self.stdout.write("Superuser %s created successfully.\n" % user)

