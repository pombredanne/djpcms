from djpcms.apps.included.admin import AdminApplication

from .models import User,ObjectPermission


admin_urls = (
              AdminApplication('/users/',
                               User,
                               list_display = ('username','email','is_active','is_superuser')),
              AdminApplication('/permissions/',
                               ObjectPermission,
                               name = 'Object Permissions',
                               list_display = ['model','object','code','numeric_code']),
            )

