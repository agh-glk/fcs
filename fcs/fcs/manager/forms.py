from django import forms
from django.forms.widgets import PasswordInput, DateTimeInput, TextInput
from models import CrawlingType, Task, User


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50, widget=TextInput())
    password = forms.CharField(max_length=50, widget=PasswordInput())


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(max_length=50, widget=PasswordInput())
    password = forms.CharField(max_length=50, widget=PasswordInput())
    password_again = forms.CharField(max_length=50, widget=PasswordInput())

    def clean(self):
        super(forms.Form, self).clean()
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password_again')
        if password1 != password2:
            raise forms.ValidationError("Provided passwords are different!")
        return self.cleaned_data


class EditTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        exclude = ['name', 'user', 'type', 'active', 'finished', 'created']


class CreateTaskForm(forms.Form):
    name = forms.CharField(max_length=100)
    priority = forms.IntegerField(min_value=1)
    whitelist = forms.CharField(max_length=250)
    blacklist = forms.CharField(max_length=250, required=False)
    max_links = forms.IntegerField(min_value=1)
    expire = forms.DateTimeField(widget=DateTimeInput())
    type = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=CrawlingType.CRAWLING_TYPES_CHOICES)


class IncreaseQuotaForm(forms.Form):
    max_priority = forms.IntegerField()
    priority_pool = forms.IntegerField()
    max_tasks = forms.IntegerField()
    link_pool = forms.IntegerField()


class EditUserForm(forms.ModelForm):

    def clean(self):
        super(forms.ModelForm, self).clean()
        if not self.cleaned_data.get('email'):
            raise forms.ValidationError('Email cannot be empty!')
        return self.cleaned_data

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

