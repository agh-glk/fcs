from django import forms
from django.forms.widgets import PasswordInput, SplitDateTimeWidget
from models import CrawlingType, CRAWLING_TYPES_CHOICES, Task


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=50)
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
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


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50)
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
            raise forms.ValidationError("Two different passwords!")
        return self.cleaned_data


class EditTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        exclude = ['name', 'user', 'type', 'active', 'finished']


class CreateTaskForm(forms.Form):
    name = forms.CharField(max_length=100)
    priority = forms.IntegerField()
    whitelist = forms.CharField(max_length=250)
    blacklist = forms.CharField(max_length=250)
    max_links = forms.IntegerField()
    expire = forms.DateTimeField(widget=SplitDateTimeWidget(date_format='%Y-%m-%d', time_format='%H:%M'))
    type = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=CRAWLING_TYPES_CHOICES)


class IncreaseQuotaForm(forms.Form):
    max_priority = forms.IntegerField()
    priority_pool = forms.IntegerField()
    max_tasks = forms.IntegerField()
    link_pool = forms.IntegerField()