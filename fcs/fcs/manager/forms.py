from django import forms
from django.forms.widgets import PasswordInput, DateTimeInput
from fcs.manager.models import QuotaException
from models import Task
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML, Field


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
        exclude = ['name', 'user', 'start_links', 'created', 'active', 'server', 'last_server_spawn', 'finished',
                   'last_data_download', 'autoscale_change']

    def is_valid(self):
        try:
            return super(EditTaskForm, self).is_valid()
        except QuotaException as e:
            self._errors[forms.forms.NON_FIELD_ERRORS] = [e.message]


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


class TaskFilterForm(forms.Form):
    ALL = 0
    RUNNING = 1
    PAUSED = 2
    FINISHED = 3
    tasks = forms.ChoiceField(choices=[(ALL, 'All'), (RUNNING, 'Running'), (PAUSED, 'Paused'), (FINISHED, 'Finished')],
                                required=False)
    page_size = forms.ChoiceField(choices=[(1, 1), (5, 5), (10, 10), (15, 15), (25, 25), (50, 50)], required=False)

    def __init__(self, *args, **kwargs):
        super(TaskFilterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.form_method = 'get'
        self.helper.form_action = ''
        self.helper.layout = Layout(
            HTML("<label class='control-label'>Tasks</label>"),
            'tasks',
            HTML("<label class='control-label'>Page size</label>"),
            'page_size',
            Submit('submit', 'Filter', css_class='btn-default'),
        )
