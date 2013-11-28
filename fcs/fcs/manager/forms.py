from oauthlib.oauth2.ext import django
from django import forms
from django.forms.widgets import PasswordInput


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(max_length=50, widget=PasswordInput())
    password_again = forms.CharField(max_length=50, widget=PasswordInput())
    email = forms.EmailField(max_length=50)
    quota = forms.IntegerField()

    def is_valid(self):
        #if self['password'] != self['password_again']:
        #    self.errors['password'] = forms.util.ErrorList(['Two different passwords.'])
        return super(forms.Form, self).is_valid()




