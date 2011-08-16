from djpcms.apps.included.admin import AdminApplication, \
                                        AdminApplicationSimple, TabViewMixin
from djpcms.apps.included.user import UserApplicationWithFilter, RegisterForm 

from .models import User,ObjectPermission, Role, Group, Log
from .forms import RoleForm, GroupForm, PermissionForm


NAME = 'Users and Permissions'

class UserAdmin(TabViewMixin,UserApplicationWithFilter):
    inherit = True
    
    def registration_done(self):
        pass


admin_urls = (
    UserAdmin('/users/',
              User,
              name = 'Users',
              list_display = ('username','first_name','last_name',
                              'email','is_active','is_superuser')),
    AdminApplication('/groups/',
                     Group,
                     form = GroupForm,
                     list_display = ('name','description')),
    AdminApplication('/roles/',
                     Role,
                     form = RoleForm,
                     name = 'Roles',
                     list_display = ('action','numeric_code',
                                     'model_type','object')),
    AdminApplication(
             '/permissions/',
             ObjectPermission,
             form = PermissionForm,
             name = 'Object Permissions',
             list_display = ['role','user','group','action']),
    AdminApplicationSimple(
               '/logs/',
               Log,
               name='Logs',
               list_display = ('timestamp','level','source',
                               'msg','host','user'),
               object_display = ('timestamp','level','source',
                                 'host','msg')
               )
)

