import os
import base64
import time
import random
import hashlib
from os import urandom

from stdnet import orm
from stdnet.utils import pickle, to_bytestring, to_string

# Use the system (hardware-based) random number generator if it exists.
if hasattr(random, 'SystemRandom'):
    randrange = random.SystemRandom().randrange
else:
    randrange = random.randrange
MAX_SESSION_KEY = 18446744073709551616     # 2 << 63

UNUSABLE_PASSWORD = '!' # This will never be a valid hash


def secret_key():
    return os.environ.get('SESSION_SECRET_KEY','sk')
    

def encrypt(plaintext):
    from Crypto.Cipher import ARC4
    if not plaintext:
        return ''
    salt = urandom(settings.SALT_SIZE)
    arc4 = ARC4.new(salt + secret_key())
    prnd = smart_str(urandom(256-len(plaintext)))
    plaintext = smart_str("%3d%s" % (len(plaintext), plaintext))
    plaintext = plaintext + prnd
    return "%s$%s" % (b64encode(salt), b64encode(arc4.encrypt(plaintext)))


def decrypt(ciphertext):
    from Crypto.Cipher import ARC4
    if ciphertext:
        salt, ciphertext = map(b64decode, ciphertext.split('$'))
        arc4 = ARC4.new(salt + settings.SECRET_KEY)
        plaintext = arc4.decrypt(ciphertext)
        return plaintext[3:3+int(plaintext[:3].strip())]
    else:
        return ''


class EncodedPickledObjectField(orm.CharField):
    
    def to_python(self, value):
        encoded_data = base64.decodestring(self.data)
        pickled, tamper_check = encoded_data[:-32], encoded_data[-32:]
        if md5_constructor(pickled + os.environ.get('SESSION_SECRET_KEY')).hexdigest() != tamper_check:
            raise SuspiciousOperation("User tampered with session cookie.")
        try:
            return pickle.loads(pickled)
        except:
            return {}
        
    def serialise(self, value):
        pickled = pickle.dumps(session_dict)
        pickled_sha = md5_constructor(pickled + os.environ.get('SESSION_SECRET_KEY')).hexdigest()
        return base64.encodestring(pickled + pickled_md5)
    

def get_hexdigest(salt, raw_password):
    b = to_bytestring(salt + raw_password,errors='ignore')
    return to_string(hashlib.sha1(b).hexdigest())


def check_password(raw_password, enc_password):
    """
    Returns a boolean of whether the raw_password was correct. Handles
    encryption formats behind the scenes.
    """
    salt, hsh = enc_password.split('$')
    return hsh == get_hexdigest(salt, raw_password)


class SuspiciousOperation(Exception):
    pass


class AnonymousUser(object):
    '''Anonymous user ala django'''
    is_active = False
    is_superuser = False
    
    def is_authenticated(self):
        return False


class SessionManager(orm.Manager):
    
    def create(self):
        return self.model(id = self.new_session_id()).save()
    
    def new_session_id(self):
        "Returns session key that isn't being used."
        try:
            pid = os.getpid()
        except AttributeError:
            pid = 1
        while 1:
            sk = os.environ.get('SESSION_SECRET_KEY') or ''
            val = to_bytestring("%s%s%s%s" % (randrange(0, MAX_SESSION_KEY), pid, time.time(),sk))
            id = hashlib.sha1(val).hexdigest()
            if not self.exists(id):
                return id

    def exists(self, id):
        try:
            self.get(id = id)
        except self.model.DoesNotExist:
            return False
        return True
    
    
class UserManager(orm.Manager):
    
    def create_user(self, username, password=None, email=None, is_superuser = False):
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
                          #email=email,
                          is_superuser=is_superuser)

        user.set_password(password)
        return user.save()

    def create_superuser(self, username, password = None, email = None):
        return self.create_user(username, email, password, is_superuser = True)
    