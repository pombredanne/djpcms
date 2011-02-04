
# Main permission flags
VIEW = 10
ADD = 20
CHANGE = 30
DELETE = 40


def has(user, permission_code, obj=None, default = False):
    '''Check for permissions'''
    if user.is_superuser:
        return True
    # No object or model
    if not obj:
        if default or user.is_active:
            return permission_code <= VIEW
        else:
            return False
    else:
        return has(user, permission_code, obj, default)    


def editing(request, page, obj = None):
    '''Check for page/block editing permissions'''
    settings = request.site.settings
    editing  = settings.CONTENT_INLINE_EDITING
    canedit  = settings.DJPCMS_USER_CAN_EDIT_PAGES
    if page and editing.get('available',False):
        if has(request.user, CHANGE, page, canedit):
            return '/%s%s' % (editing.get('preurl','edit'),request.path)
    return False
    
    

        