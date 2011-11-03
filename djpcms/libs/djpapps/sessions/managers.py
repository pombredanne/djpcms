import os
import base64
import time
import random
from datetime import datetime, timedelta
from hashlib import sha1

from stdnet import orm
from stdnet.utils import pickle, to_bytestring, to_string

from .arc4 import decrypt

# Use the system (hardware-based) random number generator if it exists.
if hasattr(random, 'SystemRandom'):
    randrange = random.SystemRandom().randrange
else:
    randrange = random.randrange
MAX_SESSION_KEY = 18446744073709551616     # 2 << 63

# Default Seetings Values. Configurable in your settings file
SALT_SIZE = 8
SESSION_USER_KEY = '_auth_user_id'
SESSION_EXPIRY = 24*3600   # 1 day


UNUSABLE_PASSWORD = '!' # This will never be a valid hash
REDIRECT_FIELD_NAME = 'next'


def check_password(raw_password, enc_password):
    """Returns a boolean of whether the raw_password was correct. Handles
encryption formats behind the scenes."""
    return raw_password.encode() == decrypt(enc_password.encode(),secret_key())


class SuspiciousOperation(Exception):
    pass


class AnonymousUser(object):
    '''Anonymous user ala django'''
    is_active = False
    is_superuser = False
    
    def is_authenticated(self):
        return False


class SessionManager(orm.Manager):
    
    def create(self, expiry):
        expiry = datetime.now() + timedelta(seconds = expiry)
        return self.model(id = self.new_session_id(),
                          expiry = expiry).save()
    
    def new_session_id(self):
        "Returns session key that isn't being used."
        try:
            pid = os.getpid()
        except AttributeError:
            pid = 1
        while 1:
            sk = os.environ.get('SESSION_SECRET_KEY') or ''
            val = to_bytestring("%s%s%s%s" % (randrange(0, MAX_SESSION_KEY),
                                              pid, time.time(),sk))
            id = sha1(val).hexdigest()
            if not self.exists(id):
                return id

    def exists(self, id):
        try:
            self.get(id = id)
        except self.model.DoesNotExist:
            return False
        return True
    
    
class UserManager(orm.Manager):
    
    def create_user(self, username, password=None, email=None,
                    is_superuser = False):
        if email:
            try:
                email_name, domain_part = email.strip().split('@', 1)
            except ValueError:
                pass
            else:
                email = '@'.join([email_name, domain_part.lower()])
        else:
            email = ''

        user = self.model(username=username,
                          email=email,
                          is_superuser=is_superuser)

        user.set_password(password)
        return user.save()

    def create_superuser(self, username, password = None, email = None):
        return self.create_user(username, password, email, is_superuser = True)
    
