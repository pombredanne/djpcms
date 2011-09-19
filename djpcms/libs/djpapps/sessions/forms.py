from djpcms import forms, html, PERMISSION_LIST
from djpcms.core.orms import registered_models_tuple
from djpcms.apps.included import search

from .models import Role, User, Group


def get_models(bfield):
    return sorted(registered_models_tuple(), key = lambda x : x[1])


class RoleForm(forms.Form):
    numeric_code = forms.ChoiceField(choices = PERMISSION_LIST,
                                     label = 'permission')
    model_type = forms.ChoiceField(choices = get_models,
                                   label = 'model')
    
    
class GroupForm(forms.Form):
    name = forms.CharField()
    description = forms.CharField(widget = html.TextArea(),
                                  required = False)
        
    
class PermissionForm(forms.Form):
    '''To use this form, full text search must be implemented on the user.'''
    role = forms.ChoiceField(choices = lambda x : Role.objects.all())
    user = forms.ChoiceField(choices = search.Search(model = User),
                             autocomplete = True,
                             required=  False)
    group = forms.ChoiceField(choices = lambda x : Group.objects.all(),
                              required = False)
    
    def clean(self):
        cd = self.cleaned_data
        user = cd.get('user',None)
        group = cd.get('group',None)
        if not user and not group:
            raise forms.ValidationError('User or group should be provided')
        elif user and group:
            raise forms.ValidationError(
                    'Either user or group should be provided')
    

class UserForm(forms.Form):
    first_name = forms.CharField()
    second_name = forms.CharField()
    email = forms.CharField()
