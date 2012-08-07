from djpcms import forms, html
from djpcms.forms import layout as uni


class LoginForm(forms.Form):
    '''The Standard login form
    '''
    username = forms.CharField(max_length=30,
                    widget=html.TextInput(cn='autocomplete-off'))
    password = forms.CharField(max_length=60, widget=html.PasswordInput())

    def clean(self):
        '''process login'''
        data = self.cleaned_data
        try:
            user = self.request.view.permissions.authenticate_and_login(
                                self.request.environ, **data)
            if user:
                data['user'] = user
                return
        except ValueError as e:
            raise forms.ValidationError(str(e))

        raise ValueError('No authentication backend available.')

    def on_submit(self, commit):
        return self.cleaned_data['user']


class LogoutForm(forms.Form):

    def on_submit(self, commit):
        if self.request:
            if self.request.view.permissions.logout(self.request.environ):
                return True
        raise ValueError('Could not logout')


class PasswordChange(forms.Form):
    password = forms.CharField(max_length=32,
                               widget=html.PasswordInput())
    re_type = forms.CharField(max_length=32,
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


class PasswordChangeForm(PasswordChange):

    def on_submit(self, commit):
        request = self.request
        user = self.user
        if request:
            User = request.view.User
            if User and isinstance(self.instance, User.model):
                user = self.instance
        pe = self.request.view.permissions
        pe.set_password(user, self.cleaned_data['password'])
        return user


class RegisterForm(PasswordChange):
    '''use this form for a simple user registration with *username*,
*password* and *password confirmation*.'''
    username = forms.CharField(max_length=32)
    #email_address = forms.CharField(
    #                    help_text="This will be used for confirmation only.")

    def clean_username(self, value):
        '''Username must be unique and without spaces'''
        value = value.replace(' ','').lower()
        if not value:
            raise forms.ValidationError('Please provide a username')
        elif self.mapper.filter(username=value):
            raise forms.ValidationError('Username "{0}" is not available.\
 Choose a different one.'.format(value))
        return value

    def clean(self):
        return self.double_check_password()

    def on_submit(self, commit):
        '''Create the new user.'''
        cd = self.cleaned_data
        pe = self.request.view.permissions
        return pe.create_user(username=cd['username'],
                              password=cd['password'])


class UserChangeForm(forms.Form):
    '''A form for editing the user details. This assume that the user
model has the fields in this form.'''
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email_address = forms.CharField(required=False)
    is_superuser = forms.BooleanField()
    is_active = forms.BooleanField(initial=True)

    def __init__(self, **kwargs):
        super(UserChangeForm, self).__init__(**kwargs)
        if not self.is_bound:
            user = self.user
            if not user or not user.is_superuser:
                self.dfields['is_superuser'].widget.addClass('hidden')
                self.dfields['is_active'].widget.addClass('hidden')


class UserAddForm(RegisterForm, UserChangeForm):
    pass


def change_password_message(request, user):
    if request.user == user:
        return '%s, you have successfully changed your password.' % user
    else:
        return 'Successfully changed password for %s.' % user

############################################################## FORM LAYOUTS

HtmlLoginForm = forms.HtmlForm(
    LoginForm,
    success_message = lambda request, user:\
     '%s successfully signed in' % user,
    inputs = (('Sign in','login_user'),)
)

HtmlLogoutForm = forms.HtmlForm(
    LogoutForm,
    layout=uni.SimpleLayout(html.Div(key='logout')),
    inputs=(('logout', 'logout'),)
)

HtmlAddUserForm = forms.HtmlForm(
    UserAddForm,
    layout = uni.FormLayout(uni.Fieldset('username','password','re_type')),
    success_message = lambda request, user:\
        'User "%s" successfully created.' % user,
    inputs = (('create','create'),)
)

HtmlRegisterForm = forms.HtmlForm(
    RegisterForm,
    layout = uni.FormLayout(uni.Fieldset('username','password','re_type')),
    success_message = lambda request, user:\
        'User %s successfully registered.' % user,
    inputs = (('register','create'),)
)

HtmlChangePassword = forms.HtmlForm(
    PasswordChangeForm,
    success_message = change_password_message,
    inputs = (('change','change'),)
)

HtmlUserChangeForm = forms.HtmlForm(
    UserChangeForm,
    inputs = (('update', 'update'),)
)