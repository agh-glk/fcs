from django import forms
from fcs.manager.models import User
from django.forms import TextInput, PasswordInput


class LoginForm(forms.Form):
    identification = forms.CharField(max_length=50, widget=TextInput())
    password = forms.CharField(max_length=50, widget=PasswordInput())
    remember_me = forms.BooleanField()


class EditUserForm(forms.ModelForm):

    def clean(self):
        super(forms.ModelForm, self).clean()
        if not self.cleaned_data.get('email'):
            raise forms.ValidationError('Email cannot be empty!')
        return self.cleaned_data

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']