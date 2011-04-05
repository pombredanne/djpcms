from djpcms import forms
from .models import PERMISSION_CODES


def get_permissions():
    return PERMISSION_CODES.items()

def get_models():
    return []


class RoleForm(forms.Form):
    permission = forms.ChoiceField(choices = get_permissions)
    model = forms.ChoiceField(choices = get_models)
    
    
class PermissionForm(forms.Form):
    permission = forms.ChoiceField(choices = get_permissions)
    model = forms.ChoiceField(choices = get_models)