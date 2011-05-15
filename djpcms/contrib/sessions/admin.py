from djpcms.apps.included.admin import AdminApplication

from .models import ObjectPermission


admin_urls = (
              AdminApplication('/permissions/',
                               ObjectPermission,
                               name = 'Object Permissions',
                               list_display = ['model','object','code','numeric_code']),
            )