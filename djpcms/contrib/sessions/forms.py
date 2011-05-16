from djpcms import forms
from .models import PERMISSION_LIST, Role, User, Group


def get_models(bfield):
    return []


class RoleForm(forms.Form):
    permission = forms.ChoiceField(choices = PERMISSION_LIST)
    model = forms.ChoiceField(choices = get_models)    
    
    
class GroupForm(forms.Form):
    name = forms.CharField()
    description = forms.CharField(widget = forms.TextArea,
                                  required = False)
        
    
class PermissionForm(forms.Form):
    role = forms.ChoiceField(choices = Role.objects.all)
    user = forms.ChoiceField(choices = User.objects.all)
    group = forms.ChoiceField(choices = Group.objects.all)
    

class UserForm(forms.Form):
    first_name = forms.CharField()
    second_name = forms.CharField()
    email = forms.CharField()
    