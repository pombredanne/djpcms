from stdnet import orm
from stdnet.utils import encoders

from djpcms.apps import PERMISSION_CODES, PERMISSION_LIST

from .managers import *


class Role(orm.StdModel):
    numeric_code = orm.IntegerField()
    model_type = orm.ModelField()
    object_id = orm.SymbolField(required = False)
    
    @property
    def object(self):
        if self.object_id:
            return None
        
    @property
    def action(self):
        return PERMISSION_CODES.get(self.numeric_code,'UNKNOWN')
    
    def __unicode__(self):
        return self.action  
    
   
class User(orm.StdModel):
    username = orm.SymbolField(unique = True)
    password = orm.CharField(required = True)
    first_name = orm.CharField()
    last_name = orm.CharField()
    email = orm.CharField()
    is_active = orm.BooleanField(default = True)
    is_superuser = orm.BooleanField(default = False)
    data = orm.JSONField(sep = '_')
    
    objects = UserManager()
    
    def __unicode__(self):
        return self.username
    
    def is_authenticated(self):
        return True
    
    def set_password(self, raw_password):
        if raw_password:
            p = encrypt(raw_password.encode(), secret_key())
            self.password = p.decode()
        else:
            self.set_unusable_password()
            
    def set_unusable_password(self):
        # Sets a value that will never be a valid hash
        self.password = UNUSABLE_PASSWORD
            
    def check_password(self, raw_password):
        """Returns a boolean of whether the raw_password was correct."""
        return check_password(raw_password, self.password)
    
    @classmethod
    def login(cls, request, user):
        pass
    
    @classmethod
    def logout(cls, request):
        pass
    

class Group(orm.StdModel):
    '''simple group'''
    name  = orm.SymbolField(unique = True)
    users = orm.ManyToManyField(User, related_name = 'groups')
    description = orm.CharField()

    
class ObjectPermission(orm.StdModel):
    '''A general permission model'''
    role = orm.ForeignKey(Role)
    user = orm.ForeignKey(User, required = False)
    group = orm.ForeignKey(Group, required = False)
    
    @property
    def action(self):
        return self.role.action
    
    
class Session(orm.StdModel):
    '''A simple session model with instances living in Redis.'''
    TEST_COOKIE_NAME = 'testcookie'
    TEST_COOKIE_VALUE = 'worked'
    id = orm.SymbolField(primary_key=True)
    data = orm.HashField(pickler=encoders.PythonPickle())
    expiry = orm.DateTimeField(index = False)
    modified = True
    
    objects = SessionManager()
    
    def __unicode__(self):
        return self.id
    
    @property
    def expired(self):
        return datetime.now() >= self.expiry
    
    def get_userid(self):
        return self[SESSION_USER_KEY]
    def set_userid(self, uid): 
        self[SESSION_USER_KEY] = uid
    user_id = property(get_userid,set_userid) 
    
    def __contains__(self, key):
        return key in self.data
    
    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, val):
        self.data[key] = val
        self.data.save()
        
    def __delitem__(self, key):
        del self.data[key]
        self.data.save()

    def set_test_cookie(self):
        self[self.TEST_COOKIE_NAME] = self.TEST_COOKIE_VALUE

    def test_cookie_worked(self):
        return self.get(self.TEST_COOKIE_NAME) == self.TEST_COOKIE_VALUE

    def delete_test_cookie(self):
        del self[self.TEST_COOKIE_NAME]
    

class Log(orm.StdModel):
    '''A database log entry'''
    timestamp = orm.DateTimeField(default=datetime.now)
    level = orm.SymbolField()
    msg = orm.CharField()
    source = orm.CharField()
    host = orm.CharField()
    user = orm.SymbolField(required=False)
    client = orm.CharField()

    class Meta:
        ordering = '-timestamp'
        
    def abbrev_msg(self, maxlen=500):
        if len(self.msg) > maxlen:
            return '%s ...' % self.msg[:maxlen]
        return self.msg
    abbrev_msg.short_description = 'abbreviated msg'
    
    
class WebAccount(orm.StdModel):
    '''
    This model can be used to store log-in information
    for a web-account. The log-in details such as username, password pin number etc...
    are encrypted and saved into the database as an encrypted string
    '''
    user   = orm.ForeignKey(User)
    name   = orm.CharField()
    url    = orm.CharField()
    e_data = orm.CharField()
        
    def __unicode__(self):
        return '%s - %s' % (self.name, self.url)

    def encrypted_property(name):
        return property(get_value(name), set_value(name))
    
    def __get_data(self):
        if self.e_data:
            return decrypt(self.e_data)
        else:
            return ''
    def __set_data(self, value):
        if value:
            svalue = encrypt(value)
        else:
            svalue = ''
        self.e_data = svalue
    data   = property(__get_data,__set_data)


    