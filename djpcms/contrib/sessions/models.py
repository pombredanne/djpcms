from stdnet import orm

from .managers import *


class Role(orm.StdModel):
    numeric_code = orm.IntegerField()
    object_or_model = orm.SymbolField()
    
    
class ObjectPermission(orm.StdModel):
    '''A general permission model'''
    role = orm.ForeignKey(Role)
    group_or_user = orm.SymbolField()
    
   
class User(orm.StdModel):
    username = orm.SymbolField(unique = True)
    password = orm.CharField(required = True)
    is_active = orm.BooleanField(default = True)
    is_superuser = orm.BooleanField(default = False)
    
    objects = UserManager()
    
    def __unicode__(self):
        return self.username
    
    def is_authenticated(self):
        return True
    
    def set_password(self, raw_password):
        if raw_password:
            salt = get_hexdigest(str(random.random()), str(random.random()))[:5]
            hsh = get_hexdigest(salt, raw_password)
            self.password = '%s$%s' % (salt, hsh)
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


class Session(orm.StdModel):
    '''A simple session model with instances living in Redis.'''
    TEST_COOKIE_NAME = 'testcookie'
    TEST_COOKIE_VALUE = 'worked'
    id = orm.SymbolField(primary_key=True)
    data = orm.HashField()
    started = orm.DateTimeField(index = False, required = False)
    expiry = orm.DateTimeField(index = False, required = False)
    expired = orm.BooleanField(default = False)
    modified = True
    
    objects = SessionManager()
    
    def __str__(self):
        return self.id
    
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
    