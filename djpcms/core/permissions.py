
VIEW_PERMISSION = 1
ADD_PERMISSION = 2
CHANGE_PERMISSION = 3
DELETE_PERMISSION = 4


def has_permission(user,
                   permission_code,
                   obj=None,
                   default = False):
    if user.is_superuser:
        return True
    # No object or model
    if not obj:
        if default or user.is_active:
            return permission_code <= VIEW_PERMISSION
        else:
            return False
    else:
        return has_permission(user, permission_code, obj, default)    


def inline_editing(request, page, obj = None):
    settings = request.site.settings
    editing  = settings.CONTENT_INLINE_EDITING
    canedit  = settings.DJPCMS_USER_CAN_EDIT_PAGES
    if page and editing.get('available',False):
        if has_permission(request.user, CHANGE_PERMISSION, page, canedit):
            return '/%s%s' % (editing.get('preurl','edit'),request.path)
    return False
    
    

        