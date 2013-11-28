from django import forms
from django.forms.widgets import PasswordInput


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(max_length=50, widget=PasswordInput())
    password_again = forms.CharField(max_length=50, widget=PasswordInput())
    email = forms.EmailField(max_length=50)
    quota = forms.IntegerField()

    def clean(self):
        super(forms.Form, self).clean()
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password_again')
        if password1 != password2:
            raise forms.ValidationError("Two different passwords!")
        return self.cleaned_data




