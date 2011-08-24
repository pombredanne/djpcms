from djpcms import sites, forms, html

from .orm import create_user, authenticate, login


class LoginForm(forms.Form):
    '''The Standard login form
    '''
    username   = forms.CharField(max_length=30,
                                 widget=html.TextInput(default_class = 'autocomplete-off'))
    password   = forms.CharField(max_length=60,widget=html.PasswordInput())
    
    def clean(self):
        '''process login
        '''
        data = self.cleaned_data
        request = self.request
        msg  = ''
        username = data.get('username',None)
        password = data.get('password',None)
        User = sites.User
        if not User:
            raise forms.ValidationError('No user')
        user = authenticate(User, username = username, password = password)
        if user is not None and user.is_authenticated():
            if user.is_active:
                login(User,request,user)
                try:
                    request.session.delete_test_cookie()
                except:
                    pass
                data['user'] = user
                return data
            else:
                msg = '%s is not active' % username
        else:
            msg = 'username or password not recognized'
        raise forms.ValidationError(msg)
    
    def save(self,commit=True):
        return self.cleaned_data['user']
    save_as_new = save
    

class PasswordChangeForm(forms.Form):
    password = forms.CharField(max_length=32,
                               widget=html.PasswordInput())
    re_type  = forms.CharField(max_length=32,
                               widget=html.PasswordInput(),
                               label="Re-enter password")
    
    def clean(self):
        if not self.user:
            raise forms.ValidationError('Not logged in')
        return self.double_check_password()
    
    def double_check_password(self):
        data     = self.cleaned_data
        password = data.get("password")
        re_type  = data.get("re_type")
        if password != re_type:
            errors = self.errors
            err = "Password didn't match. Please try again."
            if 're_type' in errors:
                errors["re_type"].append(err)
            else:
                errors["re_type"] = [err]
            try:
                del data["re_type"]
            except:
                pass
        return data
    
    def save(self, commit = True):
        self.user.set_password(self.cleaned_data['password'])
        self.user.save()
        return self.user
        
 
class RegisterForm(PasswordChangeForm):
    username = forms.CharField(max_length=32)
    #email_address = UniqueEmail(help_text="This will be used for confirmation only.")
    
    def clean_username(self, value):
        '''Username must be unique and without spaces'''
        value = value.replace(' ','')
        if not value:
            raise forms.ValidationError('Please provide a username')
        elif self.mapper.filter(username = value):
            raise forms.ValidationError('Not available')
        return value
    
    def clean(self):
        return self.double_check_password()
    
    def save(self, commit = True):
        '''Create the new user.'''
        cd = self.cleaned_data
        return create_user(self.mapper,cd['username'],cd['password'])
    

class UserChangeForm(forms.Form):
    first_name = forms.CharField(required = False)
    last_name = forms.CharField(required = False)
    email = forms.CharField(required = False)
    is_superuser = forms.BooleanField(required = False)
    is_active = forms.BooleanField(required = False)
    
