'''Very general permission model
'''
from inspect import isclass
from stdnet import orm

from djpcms.apps import PERMISSION_CODES


class Role(orm.StdModel):
    numeric_code = orm.IntegerField()
    object_or_model = orm.SymbolField()
    
    
class ObjectPermission(orm.StdModel):
    '''A general permission model'''
    role = orm.ForeignKey(Role)
    group_or_user = orm.SymbolField()
    
    
class PermissionBackend(object):
    
    def has(self, request, permission_code, obj, user = None):
        if not obj:
            return None 
        if isclass(obj):
            model = obj
            obj = None
        else:
            model = obj.__class__
        p = ObjectPermission.objects.filter(permission_model = model)
        if not p.count():
            return None