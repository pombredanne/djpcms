from djpcms import sites, forms

from .orm import create_user, authenticate, login


class LoginForm(forms.Form):
    '''The Standard login form
    '''
    username   = forms.CharField(max_length=30,
                                 widget=forms.TextInput(cn = 'autocomplete-off'))
    password   = forms.CharField(max_length=60,widget=forms.PasswordInput)
    
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
                login(User,request, user)
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
    

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=32)
    password = forms.CharField(max_length=32,
                               widget=forms.PasswordInput)
    re_type  = forms.CharField(max_length=32,
                               widget=forms.PasswordInput,
                               label="Re-enter password")
    #email_address = UniqueEmail(help_text="This will be used for confirmation only.")
    
    def clean_username(self, value):
        '''Username must be unique and without spaces'''
        value = value.replace(' ','')
        if not value:
            raise forms.ValidationError('Empty')
        elif self.mapper.filter(username = value):
            raise forms.ValidationError('Not available')
        return value
    
    def clean(self):
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
        '''Create the new user.'''
        cd = self.cleaned_data
        return create_user(self.mapper,cd['username'],cd['password'])
    

#class ForgotForm(forms.Form):
#    your_email = forms.EmailField()
    

class PasswordChangeForm(RegisterForm):
    pass
    
