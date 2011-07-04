from djpcms import forms, html
from djpcms.core.orms import registered_models_tuple

from .models import PERMISSION_LIST, Role, User, Group


def get_models(bfield):
    return sorted(registered_models_tuple(), key = lambda x : x[1])


class RoleForm(forms.Form):
    permission = forms.ChoiceField(choices = PERMISSION_LIST)
    model = forms.ChoiceField(choices = get_models)    
    
    
class GroupForm(forms.Form):
    name = forms.CharField()
    description = forms.CharField(widget = html.TextArea(),
                                  required = False)
        
    
class PermissionForm(forms.Form):
    role = forms.ChoiceField(choices = Role.objects.all)
    user = forms.ChoiceField(choices = User.objects.all)
    group = forms.ChoiceField(choices = Group.objects.all)
    

class UserForm(forms.Form):
    first_name = forms.CharField()
    second_name = forms.CharField()
    email = forms.CharField()
