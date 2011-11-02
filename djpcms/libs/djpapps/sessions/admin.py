'''Admin, requires djpcms'''
from djpcms.apps.included.admin import AdminApplication, \
                                        AdminApplicationSimple, TabViewMixin
from djpcms.apps.included.user import UserApplicationWithFilter, RegisterForm 

from .models import User, ObjectPermission, Role, Group, Session
from .forms import RoleForm, GroupForm, PermissionForm


NAME = 'Authentication'

class UserAdmin(TabViewMixin,UserApplicationWithFilter):
    inherit = True
    
    def registration_done(self):
        pass


admin_urls = (
    UserAdmin('/users/',
              User,
              name = 'users',
              list_display = ('username','first_name','last_name',
                              'email','is_active','is_superuser')),
    AdminApplication('/groups/',
                     Group,
                     name = 'groups',
                     form = GroupForm,
                     list_display = ('name','description')),
    AdminApplication('/roles/',
                     Role,
                     name = 'roles',
                     form = RoleForm,
                     list_display = ('action','numeric_code',
                                     'model_type','object')),
    AdminApplication(
             '/permissions/',
             ObjectPermission,
             name = 'permissions',
             form = PermissionForm,
             list_display = ['role','user','group','action']),
    AdminApplicationSimple(
               '/sessions/',
               Session,
               name='sessions',
               list_display = ('id','expiry')
               ),
)

