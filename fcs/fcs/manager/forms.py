from django import forms
from django.forms.widgets import PasswordInput, DateTimeInput
from fcs.manager.models import QuotaException
from models import Task
from django.core.exceptions import ValidationError


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
        exclude = ['name', 'user', 'start_links', 'created', 'active', 'server', 'last_server_spawn', 'finished', 'last_data_download']


class CreateTaskForm(forms.Form):
    name = forms.CharField(max_length=100)
    priority = forms.IntegerField(min_value=1)
    start_links = forms.CharField(max_length=1000, widget=forms.Textarea())
    whitelist = forms.CharField(max_length=250, required=False)
    blacklist = forms.CharField(max_length=250, required=False)
    max_links = forms.IntegerField(min_value=1)
    expire = forms.DateTimeField(widget=DateTimeInput())
    mime_type = forms.CharField(max_length=250, initial='text/html')

    def __init__(self, user=None, *args, **kwargs):
        super(CreateTaskForm, self).__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned_data = super(CreateTaskForm, self).clean()
        task = Task(user=self.user, name=cleaned_data.get('name'), whitelist=cleaned_data.get('whitelist'),
                    blacklist=cleaned_data.get('blacklist'), max_links=cleaned_data.get('max_links'),
                    expire_date=cleaned_data.get('expire'), priority=cleaned_data.get('priority'),
                    mime_type=cleaned_data.get('mime_type'), start_links=cleaned_data.get('start_links'))
        try:
            task.clean()
        except QuotaException as e:
            raise ValidationError(e.message)
        return self.cleaned_data
