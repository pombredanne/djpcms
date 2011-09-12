from stdnet import orm
from stdnet.utils import encoders

from djpcms import PERMISSION_CODES

from .managers import *


class Role(orm.StdModel):
    '''A role is an association with an action and a model
or an instance of a model.'''
    numeric_code = orm.IntegerField()
    model_type = orm.ModelField()
    object_id = orm.SymbolField(required = False)
    
    @property
    def object(self):
        if not hasattr(self,'_object'):
            if not self.object_id:
                obj = None
            else:
                obj = self.model_type.objects.get(id = self.object_id)
            self._object = obj
        return self._object
        
    @property
    def action(self):
        return PERMISSION_CODES.get(self.numeric_code,'UNKNOWN')
    
    def __unicode__(self):
        obj = self.object or self.model_type
        return '{0} - {1}'.format(self.action,obj)
    
   
class User(orm.StdModel):
    username = orm.SymbolField(unique = True)
    password = orm.CharField(required = True, hidden = True)
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
    
    def __unicode__(self):
        return self.name

    
class ObjectPermission(orm.StdModel):
    '''A general permission model. It associates a Role to a user or a group'''
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
    
    
