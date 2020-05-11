from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from user_accounts.models import User
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = User
        fields = '__all__'
        widgets = {
            'phonenumber': forms.TextInput(attrs={'style': 'color:white'})
        }


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        models = User
        fields = '__all__'


class UserForm(forms.Form):
    password = forms.CharField(label='Password', max_length=128)
    email = forms.EmailField(label='Email address',
                             max_length=254, required=False)
    phonenumber = PhoneNumberField(widget=PhoneNumberInternationalFallbackWidget)
    username = forms.CharField(label='Username', max_length=20)
    first_name = forms.CharField(label='First name', max_length=20)
    last_name = forms.CharField(label='Last name', max_length=20)
    otp = forms.CharField(label='Otp', max_length=20)


class LoginForm(AuthenticationForm):
    phonenumber = PhoneNumberField(widget=PhoneNumberInternationalFallbackWidget)
    password = forms.CharField(label="Password", max_length=32, widget=forms.TextInput(
        attrs={'type': 'password', 'id': 'password'}))


class Password_reset(forms.Form):
    phonenumber = PhoneNumberField(widget=PhoneNumberInternationalFallbackWidget)

    def user_in_site_validator(self):
        people = User.objects.all()
        if self.phonenumber not in people:
            raise forms.ValidationError("""{phonenumber} is not in the system""")


class PasswordChange(forms.Form):
    password = forms.CharField(max_length=14, widget=forms.PasswordInput)
    new_password = forms.CharField(max_length=14, widget=forms.PasswordInput)
