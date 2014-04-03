from django import forms
from django.forms.widgets import PasswordInput, DateTimeInput, TextInput
from models import CrawlingType, Task
from django.core.exceptions import ValidationError
from django.db.models.aggregates import Sum


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
        exclude = ['name', 'user', 'type', 'created', 'active', 'finished', 'last_data_download']


class CreateTaskForm(forms.Form):
    name = forms.CharField(max_length=100)
    priority = forms.IntegerField(min_value=1)
    whitelist = forms.CharField(max_length=250)
    blacklist = forms.CharField(max_length=250, required=False)
    max_links = forms.IntegerField(min_value=1)
    expire = forms.DateTimeField(widget=DateTimeInput())
    type = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=CrawlingType.CRAWLING_TYPES_CHOICES)

    def __init__(self, user=None, *args, **kwargs):
        super(CreateTaskForm, self).__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned_data = super(CreateTaskForm, self).clean()
        priority = cleaned_data.get('priority')
        if priority <= 0:
            raise ValidationError('Priority must be positive')
        max_links = cleaned_data.get('max_links')
        if max_links <= 0:
            raise ValidationError('Links amount must be positive')
        if self.user.quota.max_priority < priority:
            raise ValidationError('Task priority exceeds user quota! Limit: ' + str(self.user.quota.max_priority))
        if self.user.quota.max_tasks <= self.user.task_set.filter(finished=False).count():
            raise ValidationError('User has too many opened tasks! Limit: ' + str(self.user.quota.max_tasks))
        if self.user.quota.max_links < max_links:
            raise ValidationError('Task link limit exceeds user quota! Limit: ' + str(self.user.quota.max_links))

        priorities = self.user.task_set.filter(active=True).aggregate(Sum('priority'))['priority__sum']
        if self.user.quota.priority_pool < (priorities + priority if priorities else priority):
            raise ValidationError("User priority pool exceeded! Limit: " + str(self.user.quota.priority_pool))

        links = self.user.task_set.filter(finished=False).aggregate(Sum('max_links'))['max_links__sum']
        if self.user.quota.link_pool < (links + max_links if links else max_links):
            raise ValidationError("User link pool exceeded! Limit: " + str(self.user.quota.link_pool))
        return self.cleaned_data
