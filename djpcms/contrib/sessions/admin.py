from djpcms.apps.included.admin import AdminApplication, AdminApplicationSimple

from .models import User,ObjectPermission, Role, Group, Log
from .forms import RoleForm, GroupForm


NAME = 'Users and Permissions'

admin_urls = (
              AdminApplication('/users/',
                               User,
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
                               list_display = ['action','numeric_code','model_type','object']),
              AdminApplication('/permissions/',
                               ObjectPermission,
                               name = 'Object Permissions',
                               list_display = ['role','user','group','action']),
              AdminApplicationSimple('/logs/',
                                     Log,
                                     name='Logs',
                                     list_display = ('timestamp','level','source','host'),
                                     object_display = ('timestamp','level','source',
                                                       'host','msg')
                                     )
            )

